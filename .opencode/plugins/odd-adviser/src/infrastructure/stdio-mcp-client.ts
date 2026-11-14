// Concrete stdio adapter for the advisory port: one child process, connected on first use,
// plus the deferred wrapper that starts nothing until the first evaluation. Wire mapping
// stays here. A timeout does not prove cancellation; the attempt simply stops being awaited.

import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';

import { answersNoQuestion } from '../application/evaluate-evidence.ts';
import type {
  OddEvidenceAnswer,
  OddEvidenceEvaluation,
  OddEvidenceInput,
  OddEvidenceOutcome,
  OddEvidenceUnavailableCode,
} from '../domain/advisory.ts';
import type { OddEvidenceEvaluatorConnection } from '../domain/plugin-contract.ts';

export const ODD_EVIDENCE_TOOL_NAME = 'evaluate_odd_evidence';

type McpToolResult = {
  readonly isError?: boolean | undefined;
  readonly structuredContent?: unknown;
};

export type StdioMcpClientOptions = {
  readonly command: string;
  readonly args: ReadonlyArray<string>;
  readonly cwd: string;
  readonly env?: Readonly<Record<string, string>>;
  readonly toolName?: string;
};

function toToolArguments(input: OddEvidenceInput): Record<string, unknown> {
  return {
    text: input.text,
    images: input.images.map((image) => ({
      mimeType: image.mimeType,
      base64: image.base64,
    })),
    ...(input.expectedModel === undefined ? {} : { expectedModel: input.expectedModel }),
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function toProbabilities(value: unknown): Record<string, number> | null {
  if (!isRecord(value)) return null;
  const probabilities: Record<string, number> = {};
  for (const [state, score] of Object.entries(value)) {
    if (typeof score !== 'number' || !Number.isFinite(score)) return null;
    probabilities[state] = score;
  }
  return probabilities;
}

function toAnswer(value: unknown): OddEvidenceAnswer | null {
  if (!isRecord(value)) return null;
  if (value.type !== 'choice') return null;
  if (typeof value.choice !== 'string' || value.choice.length === 0) return null;
  const probabilities = toProbabilities(value.probabilities);
  if (probabilities === null) return null;
  const confidence = value.confidence;
  if (confidence === undefined) {
    return { type: 'choice', choice: value.choice, probabilities };
  }
  if (typeof confidence !== 'number' || !Number.isFinite(confidence)) return null;
  return { type: 'choice', choice: value.choice, probabilities, confidence };
}

function toAnswers(value: unknown): Record<string, OddEvidenceAnswer> | null {
  if (!isRecord(value)) return null;
  const answers: Record<string, OddEvidenceAnswer> = {};
  for (const [questionId, candidate] of Object.entries(value)) {
    const answer = toAnswer(candidate);
    if (answer === null) return null;
    answers[questionId] = answer;
  }
  return answers;
}

function toEvaluation(
  profileId: unknown,
  profileVersion: unknown,
  answers: unknown,
): OddEvidenceEvaluation | null {
  if (typeof profileId !== 'string' || profileId.length === 0) return null;
  if (
    typeof profileVersion !== 'number' ||
    !Number.isInteger(profileVersion) ||
    profileVersion <= 0
  ) {
    return null;
  }
  const validAnswers = toAnswers(answers);
  return validAnswers === null || answersNoQuestion(validAnswers)
    ? null
    : { profileId, profileVersion, answers: validAnswers };
}

function toUnavailableOutcome(code: OddEvidenceUnavailableCode): OddEvidenceOutcome {
  return { status: 'unavailable', code };
}

function toEvaluationId(value: unknown): string | undefined {
  return typeof value === 'string' && value.length > 0 ? value : undefined;
}

function withEvaluationId(
  outcome: OddEvidenceOutcome,
  evaluationId: string | undefined,
): OddEvidenceOutcome {
  return evaluationId === undefined ? outcome : { ...outcome, evaluationId };
}

export function mapMcpToolResultToOutcome(result: McpToolResult): OddEvidenceOutcome {
  if (result.isError === true) return toUnavailableOutcome('tool_error');
  const payload = result.structuredContent;
  if (!isRecord(payload)) return toUnavailableOutcome('malformed_payload');
  const evaluationId = toEvaluationId(payload.evaluationId);
  if (payload.ok === false) {
    return withEvaluationId(toUnavailableOutcome('rejected'), evaluationId);
  }
  if (payload.ok !== true) {
    return withEvaluationId(toUnavailableOutcome('malformed_payload'), evaluationId);
  }
  const evaluation = toEvaluation(payload.profileId, payload.profileVersion, payload.answers);
  return evaluation === null
    ? withEvaluationId(toUnavailableOutcome('malformed_payload'), evaluationId)
    : withEvaluationId({ status: 'evaluated', evaluation }, evaluationId);
}

type BoundedAttempt<T> =
  | { readonly kind: 'answered'; readonly result: T }
  | { readonly kind: 'failed' }
  | { readonly kind: 'elapsed' };async function boundedAttempt<T>(
  work: () => Promise<T>,
  timeoutMs: number,
): Promise<BoundedAttempt<T>> {
  const attempt: Promise<BoundedAttempt<T>> = work().then(
    (result) => ({ kind: 'answered' as const, result }),
    () => ({ kind: 'failed' as const }),
  );

  let timer: ReturnType<typeof setTimeout> | undefined;
  const elapsed = new Promise<BoundedAttempt<T>>((resolve) => {
    timer = setTimeout(() => resolve({ kind: 'elapsed' }), timeoutMs);
  });

  try {
    return await Promise.race([attempt, elapsed]);
  } finally {
    if (timer !== undefined) clearTimeout(timer);
  }
}

async function releaseFailedInitialization(
  client: Client,
  transport: StdioClientTransport,
): Promise<void> {
  // Close the client first so a half-connected session tears down before the transport, then
  // the transport itself so a child spawned by a failed handshake is released even when the
  // client never attached to it. Cleanup never replaces the connection error: each release is
  // contained and reported as a diagnostic on stderr, where this adapter's out-of-band
  // failures belong.
  for (const release of [() => client.close(), () => transport.close()]) {
    try {
      await release();
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      process.stderr.write(`odd-adviser: failed to release MCP initialization: ${detail}\n`);
    }
  }
}

export function createStdioMcpClient(
  options: StdioMcpClientOptions,
): OddEvidenceEvaluatorConnection {
  const toolName = options.toolName ?? ODD_EVIDENCE_TOOL_NAME;
  let connection: Promise<Client> | undefined;

  async function connect(): Promise<Client> {
    const client = new Client({ name: 'odd-adviser', version: '0.1.0' });
    const transport = new StdioClientTransport({
      command: options.command,
      args: [...options.args],
      cwd: options.cwd,
      ...(options.env === undefined ? {} : { env: { ...options.env } }),
    });
    try {
      await client.connect(transport);
      return client;
    } catch (error) {
      // A handshake can fail after the transport already spawned the child, so initialization
      // failure releases both before the original error reaches the caller.
      await releaseFailedInitialization(client, transport);
      throw error;
    }
  }

  // One attempt at a time: a concurrent caller reuses the attempt in flight, and a rejected
  // attempt is dropped so a later evaluation can reconnect. The slot is cleared only while it
  // still holds that attempt, so a connection started after a replacement is never discarded.
  function currentConnection(): Promise<Client> {
    if (connection !== undefined) return connection;
    const attempt = connect();
    connection = attempt;
    void attempt.catch(() => {
      if (connection === attempt) connection = undefined;
    });
    return attempt;
  }

  return {
    evaluate: async (input, evaluationOptions) => {
      const attempt = await boundedAttempt<McpToolResult>(async () => {
        const client = await currentConnection();
        return client.callTool(
          { name: toolName, arguments: toToolArguments(input) },
          { timeout: evaluationOptions.timeoutMs },
        );
      }, evaluationOptions.timeoutMs);

      if (attempt.kind === 'answered') return mapMcpToolResultToOutcome(attempt.result);
      if (attempt.kind === 'failed') return toUnavailableOutcome('transport_error');
      return toUnavailableOutcome('timeout');
    },
    close: async () => {
      const pending = connection;
      connection = undefined;
      if (pending === undefined) return;
      await pending.then(
        (client) => client.close(),
        () => undefined,
      );
    },
  };
}

export function createDeferredConnection(
  createConnection: () => OddEvidenceEvaluatorConnection,
): OddEvidenceEvaluatorConnection {
  let connection: OddEvidenceEvaluatorConnection | undefined;

  return {
    evaluate: async (input, evaluationOptions) => {
      if (connection === undefined) connection = createConnection();
      return connection.evaluate(input, evaluationOptions);
    },
    close: async () => {
      const current = connection;
      connection = undefined;
      if (current === undefined) return;
      await current.close().catch(() => undefined);
    },
  };
}

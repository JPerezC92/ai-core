// Delivery edge for the portable System 1 surface: one MCP server exposing the
// `evaluate_odd_evidence` tool. It maps tool arguments to the application operation's
// typed parameters, delegates the evaluation, and returns the typed result. It owns no
// inference policy, performs no IO, and never echoes supplied text or image data in its
// output or error messages.
//
// The handler delegates exactly once per call and projects the evaluated result onto the
// advertised output union; the rejection branch discards the domain's diagnostic reason
// because that text can quote caller-supplied values. The one piece of request metadata it
// forwards is the invoking session from `_meta`, so the operational trace can correlate an
// evaluation with the call that asked for it.

import { McpServer } from '@modelcontextprotocol/server';
import type { CallToolResult, ServerContext } from '@modelcontextprotocol/server';
import { z } from 'zod';

import { EvaluateOddEvidence } from '../application/evaluate-odd-evidence.ts';
import type { OddEvidenceEvaluation } from '../application/evaluate-odd-evidence.ts';
import type {
  OddEvidenceGateway,
  OddEvidenceImage,
  QuestionProfileSource,
} from '../domain/odd-evidence.ts';

export const ODD_EVIDENCE_TOOL_NAME = 'evaluate_odd_evidence';

// Transport bounds advertised in the tool's input schema: one call carries at most four
// inline images, and one base64 payload is capped at 4 MiB of base64 text (~3 MiB of
// image bytes). They bound the payload; they are not a claim about model behaviour.
export const MAX_ODD_EVIDENCE_IMAGES = 4;
export const MAX_ODD_EVIDENCE_IMAGE_BASE64_LENGTH = 4_194_304;

const inlineImageSchema = z.object({
  mimeType: z.string().min(1).describe('Inline image media type, for example image/png'),
  base64: z
    .string()
    .min(1)
    .max(MAX_ODD_EVIDENCE_IMAGE_BASE64_LENGTH)
    .describe('Inline image bytes, base64 encoded'),
});

// The tool input contract: the evidence text, the inline images and a per-call model
// override. The bounds live here, so an over-limit request is rejected before the
// evaluation operation runs.
const evaluateOddEvidenceInputSchema = z.object({
  text: z.string().describe('Evidence text evaluated against the versioned question profile'),
  images: z
    .array(inlineImageSchema)
    .max(MAX_ODD_EVIDENCE_IMAGES)
    .describe('Inline images supplied with the message, at most four'),
  expectedModel: z
    .string()
    .min(1)
    .optional()
    .describe('Model identifier this call expects; defaults to the configured model'),
});

// The validated result union returned by the application operation. The rejection-code
// and answer vocabularies belong to the domain, so this wire contract names the fields
// and leaves the enumerated values at their single domain owner.
const decisionAnswerSchema = z.object({
  type: z.literal('choice'),
  choice: z.string().describe('Evidence state chosen for this question'),
  probabilities: z.record(z.string(), z.number()).describe('Score per evidence state'),
  confidence: z.number().optional(),
});

const oddEvidenceEvaluationSchema = z.union([
  z.object({
    ok: z.literal(true),
    profileId: z.string().describe('Question profile identity that was evaluated'),
    profileVersion: z.number().int().positive().describe('Question profile version'),
    answers: z.record(z.string(), decisionAnswerSchema).describe('Validated answer per question'),
  }),
  z.object({
    ok: z.literal(false),
    code: z.string().describe('Stable rejection code owned by the evidence evaluation'),
    reason: z.string().describe('Rejection reason'),
  }),
]);

type EvaluateOddEvidenceRequest = z.infer<typeof evaluateOddEvidenceInputSchema>;

// The evaluator this edge depends on: the application operation's public signature,
// taken from its single home rather than restated here.
export type OddEvidenceEvaluator = Pick<EvaluateOddEvidence, 'execute'>;

export type OddEvidenceServerOptions = {
  readonly expectedModel: string;
  // The versioned question-profile artifact this surface evaluates against. The MCP
  // edge never reads it: host composition loads it and injects `questionProfileSource`,
  // and this record keeps the portable surface and its host on one configuration.
  readonly profilePath: string;
};

export type OddEvidenceServerCollaborators =
  | { readonly evaluateOddEvidence: OddEvidenceEvaluator }
  | {
      readonly decisionGateway: OddEvidenceGateway;
      readonly questionProfileSource: QuestionProfileSource;
    };

// One mapping step from the transport payload to the operation's domain parameters.
// No rule is applied here.
function toEvidenceImages(
  images: EvaluateOddEvidenceRequest['images'],
): ReadonlyArray<OddEvidenceImage> {
  return images.map((image) => ({ mimeType: image.mimeType, base64: image.base64 }));
}

// OpenCode sends the invoking session in the tool call's request metadata, so the trace can
// correlate an evaluation with the session that asked for it. The value is client-supplied:
// it is accepted only when it looks like a session identifier, and anything else is
// dropped rather than written into the operational record as free text.
const OPENCODE_SESSION_ID_META_KEY = 'ai.opencode/sessionID';
const SESSION_ID_PATTERN = /^[A-Za-z0-9_-]{1,128}$/;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function readSessionId(context: ServerContext): string | undefined {
  // The SDK surfaces the request's `_meta` on the handler context with only the reserved
  // `io.modelcontextprotocol/*` envelope keys lifted out, so a host-specific key such as
  // `ai.opencode/sessionID` is still there. It is client-supplied metadata, so it is read
  // as an unknown value and validated rather than trusted.
  const meta: unknown = context.mcpReq._meta;
  if (!isRecord(meta)) return undefined;
  const value = meta[OPENCODE_SESSION_ID_META_KEY];
  return typeof value === 'string' && SESSION_ID_PATTERN.test(value) ? value : undefined;
}

// The domain result is the payload; the text copy serves clients without structured
// content. Neither carries the supplied evidence.
function toToolResult(result: OddEvidenceEvaluation): CallToolResult {
  return {
    content: [{ type: 'text', text: JSON.stringify(result) }],
    structuredContent: result,
  };
}

// S9 bound for the rejection branch: the domain's reason is diagnostic text that may
// quote caller-supplied values (for example the expected model), so the payload carries
// one fixed reason and `code` alone identifies the failure class.
const BOUNDED_REJECTION_REASON =
  'Rejected before delivery; the rejection code identifies the failure class';

// One projection step onto the advertised output union: the success branch keeps exactly
// the profile identity and the validated answers, the rejection branch keeps only its
// code. No supplied text, image bytes or data URL can reach the payload.
function toWireEvaluation(result: OddEvidenceEvaluation): OddEvidenceEvaluation {
  return result.ok
    ? {
        ok: true,
        profileId: result.profileId,
        profileVersion: result.profileVersion,
        answers: result.answers,
      }
    : { ok: false, code: result.code, reason: BOUNDED_REJECTION_REASON };
}

// Composition at the edge: an already evaluated-operation collaborator is used as
// supplied, otherwise the concrete adapters are wired into the operation here.
function resolveEvaluator(
  collaborators: OddEvidenceServerCollaborators,
): OddEvidenceEvaluator {
  return 'evaluateOddEvidence' in collaborators
    ? collaborators.evaluateOddEvidence
    : new EvaluateOddEvidence({
        decisionGateway: collaborators.decisionGateway,
        questionProfileSource: collaborators.questionProfileSource,
      });
}

export function createOddEvidenceServer(
  collaborators: OddEvidenceServerCollaborators,
  options: OddEvidenceServerOptions,
): McpServer {
  const evaluateOddEvidence = resolveEvaluator(collaborators);
  // Handshake identity of the portable surface, reported once when a client connects.
  const server = new McpServer({ name: 'odd-adviser', version: '0.1.0' });

  server.registerTool(
    ODD_EVIDENCE_TOOL_NAME,
    {
      title: 'Evaluate ODD evidence',
      description:
        'Evaluate supplied text and inline images against the versioned ODD evidence question profile. The result is advisory: it never authorizes, waives a gate, or blocks an action.',
      inputSchema: evaluateOddEvidenceInputSchema,
      outputSchema: oddEvidenceEvaluationSchema,
    },
    async (args, context) => {
      // One delegation per call: the supplied evidence, the resolved model and the
      // invoking session reach the evaluation operation unchanged, and only its validated
      // result is returned.
      const evaluation = await evaluateOddEvidence.execute(
        args.text,
        toEvidenceImages(args.images),
        args.expectedModel ?? options.expectedModel,
        readSessionId(context),
      );
      return toToolResult(toWireEvaluation(evaluation));
    },
  );

  return server;
}

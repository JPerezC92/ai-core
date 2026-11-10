// OpenCode adapter composition root for the portable System 1 MCP surface. Domain, application
// and infrastructure modules own the captured message, the evaluation operation, the stdio
// client and the host hooks. This entry re-exports the public contract, composes a real-timer
// deadline for the three-argument `evaluateEvidence` export, and resolves default connection
// and trace paths from this module's location.

import { fileURLToPath } from 'node:url';

import { getDefaultEnvironment } from '@modelcontextprotocol/client/stdio';

import { evaluateEvidence as evaluateEvidenceAgainstDeadline } from './application/evaluate-evidence.ts';
import type { CapturedMessage } from './domain/capture-message.ts';
import type { Deadline } from './domain/deadline.ts';
import type { OddEvidenceEvaluator } from './domain/advisory.ts';
import type {
  EvaluateEvidenceOptions,
  OddEvidenceAdvisory,
} from './domain/plugin-contract.ts';
import { JsonLinesObservations } from './infrastructure/json-lines-observations.ts';
import { JsonLinesPluginEvents } from './infrastructure/json-lines-plugin-events.ts';
import { createOddAdviserPlugin } from './infrastructure/opencode-adviser.ts';
import {
  createStdioMcpClient,
  type StdioMcpClientOptions,
} from './infrastructure/stdio-mcp-client.ts';

export type {
  OddEvidenceAnswer,
  OddEvidenceEvaluation,
  OddEvidenceEvaluator,
  OddEvidenceEvaluatorOptions,
  OddEvidenceImage,
  OddEvidenceInput,
  OddEvidenceOutcome,
  OddEvidenceUnavailableCode,
} from './domain/advisory.ts';

export type {
  ObservationAssessment,
  ObservationInput,
  ObservationRecord,
  ObservationReportedFooter,
  ObservationSink,
  ObservationTool,
  ObservationToolStatus,
} from './domain/observation.ts';

export type {
  PluginEvent,
  PluginEventCode,
  PluginEventInput,
  PluginEventSink,
  PluginEventStage,
} from './domain/plugin-event.ts';

export type {
  EvaluateEvidenceOptions,
  MessageIdentity,
  OddEvidenceAdvisory,
  OddEvidenceEvaluatorConnection,
} from './domain/plugin-contract.ts';

export type {
  ContextBuildEvent,
  ContextBuildListener,
  ContextInlinedMedia,
  ContextMessage,
  ContextMessageMedia,
  ContextMessagePart,
  ContextSystemPart,
  HttpResponseEvent,
  HttpResponseListener,
  OddAdviserCleanup,
  OddAdviserHostSession,
  OddAdviserHostTool,
  OddAdviserPlugin,
  OddAdviserSetupContext,
  PromptAdmissionEvent,
  PromptAdmissionListener,
  PromptDraft,
  PromptFile,
  ToolExecuteAfterEvent,
  ToolExecuteAfterListener,
  WebSocketReceiveEvent,
  WebSocketReceiveListener,
} from './infrastructure/opencode-adviser.ts';

export type { AdmittedPart, CapturedImage, CapturedMessage } from './domain/capture-message.ts';
export { captureMessage } from './domain/capture-message.ts';

export {
  ADVISORY_BLOCK_END,
  ADVISORY_BLOCK_START,
  ADVISORY_UNAVAILABLE_BLOCK_START,
  formatAdvisoryBlock,
} from './domain/advisory-block.ts';

export type { StdioMcpClientOptions } from './infrastructure/stdio-mcp-client.ts';
export {
  ODD_EVIDENCE_TOOL_NAME,
  createStdioMcpClient,
  mapMcpToolResultToOutcome,
} from './infrastructure/stdio-mcp-client.ts';

const DEFAULT_CONNECTION_ENTRY_PATH =
  '../../../../mcp-servers/system-one/src/mcp/stdio.ts';
const DEFAULT_CONNECTION_WORKING_DIRECTORY = '../../../../';
const DEFAULT_CONNECTION_COMMAND = 'node';
const SYSTEM_ONE_ENVIRONMENT_PREFIX = 'SYSTEM_ONE_';
const EXECUTABLE_RESOLUTION_ENVIRONMENT_NAME = 'PATH';
const PLUGIN_EVENT_PATH_VARIABLE = 'ODD_ADVISER_EVENT_PATH';
const DEFAULT_PLUGIN_EVENT_RELATIVE_PATH = '../../../../output/system1/plugin.jsonl';
const TRACE_PATH_VARIABLE = 'SYSTEM_ONE_TRACE_PATH';
const DEFAULT_TRACE_RELATIVE_PATH = '../../../../output/system1/events.jsonl';

function readSystemOneEnvironment(): Readonly<Record<string, string>> {
  const environment: Record<string, string> = {};
  for (const [name, value] of Object.entries(process.env)) {
    if (!name.startsWith(SYSTEM_ONE_ENVIRONMENT_PREFIX) || value === undefined) continue;
    environment[name] = value;
  }
  return environment;
}

function readExecutableResolutionEnvironment(): Readonly<Record<string, string>> {
  const value = process.env[EXECUTABLE_RESOLUTION_ENVIRONMENT_NAME];
  return value === undefined ? {} : { [EXECUTABLE_RESOLUTION_ENVIRONMENT_NAME]: value };
}

export function createDefaultConnectionOptions(): StdioMcpClientOptions {
  return {
    command: DEFAULT_CONNECTION_COMMAND,
    args: [fileURLToPath(new URL(DEFAULT_CONNECTION_ENTRY_PATH, import.meta.url))],
    cwd: fileURLToPath(new URL(DEFAULT_CONNECTION_WORKING_DIRECTORY, import.meta.url)),
    env: {
      ...getDefaultEnvironment(),
      ...readExecutableResolutionEnvironment(),
      ...readSystemOneEnvironment(),
    },
  };
}

function resolvePluginEventPath(): string {
  const configured = process.env[PLUGIN_EVENT_PATH_VARIABLE]?.trim();
  return configured === undefined || configured.length === 0
    ? fileURLToPath(new URL(DEFAULT_PLUGIN_EVENT_RELATIVE_PATH, import.meta.url))
    : configured;
}

function resolveObservationPath(): string {
  const configured = process.env[TRACE_PATH_VARIABLE]?.trim();
  return configured === undefined || configured.length === 0
    ? fileURLToPath(new URL(DEFAULT_TRACE_RELATIVE_PATH, import.meta.url))
    : configured;
}

function createTimerDeadline(): Deadline {
  return {
    schedule(timeoutMs, onElapsed) {
      const timer = setTimeout(onElapsed, timeoutMs);
      return () => {
        clearTimeout(timer);
      };
    },
  };
}

export async function evaluateEvidence(
  message: CapturedMessage,
  evaluator: OddEvidenceEvaluator,
  options: EvaluateEvidenceOptions,
): Promise<OddEvidenceAdvisory> {
  return evaluateEvidenceAgainstDeadline(
    message,
    evaluator,
    options,
    createTimerDeadline(),
  );
}

const composed = createOddAdviserPlugin({
  createDefaultConnection: () => createStdioMcpClient(createDefaultConnectionOptions()),
  createDefaultEventSink: () =>
    new JsonLinesPluginEvents({ eventPath: resolvePluginEventPath() }),
  createDefaultObservationSink: () =>
    new JsonLinesObservations({ eventPath: resolveObservationPath() }),
});

const plugin = {
  id: composed.id,
  setup(context: Parameters<typeof composed.setup>[0]) {
    return composed.setup({
      ...context,
      ...(context.tool === undefined ? {} : { tool: { hook: context.tool.hook } }),
    });
  },
};

export default plugin;

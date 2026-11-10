#!/usr/bin/env node
// Executable entry for the portable System 1 MCP, declared as this package's `bin`: it
// reads the host configuration from the environment, composes the concrete adapters once,
// and serves the registered `evaluate_odd_evidence` tool over stdio. Composition and
// configuration live only here; the MCP surface and the evaluation operation take their
// collaborators as injected ports and own no environment access.
//
// Stdio binding: stdout carries protocol frames only. Nothing in this module writes to
// stdout; diagnostics go to stderr.

import { fileURLToPath } from 'node:url';

import { serveStdio } from '@modelcontextprotocol/server/stdio';

import { EvaluateOddEvidence } from '../application/evaluate-odd-evidence.ts';
import { ImageStore } from '../infrastructure/image-store.ts';
import { JsonLinesEvaluationTrace } from '../infrastructure/json-lines-evaluation-trace.ts';
import { LmStudioDecisionGateway } from '../infrastructure/lm-studio-decision-gateway.ts';
import { ProfileFileSource } from '../infrastructure/profile-file-source.ts';
import { createOddEvidenceServer } from './odd-evidence-server.ts';
import type { OddEvidenceServerOptions } from './odd-evidence-server.ts';

// Documented defaults, used when the corresponding environment variable is unset, blank
// or unusable.
const DEFAULT_ENDPOINT = 'http://127.0.0.1:1234';
const DEFAULT_MODEL = 'd1-2b@q8_0';
const DEFAULT_TIMEOUT_MS = 15_000;
const PROFILE_FILE_NAME = 'odd-evidence-v4.json';
// The operational trace file lives at `<package>/../../output/system1/events.jsonl`,
// resolved from this module's location: `src/mcp/stdio.ts` is four directories below the
// repository root, whose `output/` directory is gitignored. The trace's image store
// writes beside it, so one directory holds one evaluation's exchange and its bytes.
const DEFAULT_TRACE_RELATIVE_PATH = '../../../../output/system1/events.jsonl';
const DEFAULT_IMAGE_DIRECTORY_RELATIVE_PATH = '../../../../output/system1/images';

type SystemOneConfiguration = {
  readonly endpoint: string;
  readonly model: string;
  readonly profilePath: string;
  readonly timeoutMs: number;
  readonly tracePath: string;
  readonly imageDirectory: string;
};

// A blank environment value is treated as unset: an empty endpoint, model or path is not
// a usable configuration.
function readEnvironmentValue(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed === undefined || trimmed.length === 0 ? undefined : trimmed;
}

// The timeout is a transport bound, not a policy decision: an unusable value falls back
// to the documented default instead of preventing the host's server from starting.
function readTimeoutMs(value: string | undefined): number {
  const timeoutMs = Number(readEnvironmentValue(value));
  return Number.isInteger(timeoutMs) && timeoutMs > 0 ? timeoutMs : DEFAULT_TIMEOUT_MS;
}

// The package's own profile document, resolved from this module's location so the entry
// works from any working directory.
function defaultProfilePath(): string {
  return fileURLToPath(new URL(`../../profiles/${PROFILE_FILE_NAME}`, import.meta.url));
}

// The repository-root operational trace file, resolved from this module's location.
function defaultTracePath(): string {
  return fileURLToPath(new URL(DEFAULT_TRACE_RELATIVE_PATH, import.meta.url));
}

// The repository-root image directory the trace's content-addressed image store writes,
// resolved from this module's location.
function defaultImageDirectory(): string {
  return fileURLToPath(new URL(DEFAULT_IMAGE_DIRECTORY_RELATIVE_PATH, import.meta.url));
}

function readConfiguration(environment: NodeJS.ProcessEnv): SystemOneConfiguration {
  return {
    endpoint: readEnvironmentValue(environment.SYSTEM_ONE_ENDPOINT) ?? DEFAULT_ENDPOINT,
    model: readEnvironmentValue(environment.SYSTEM_ONE_MODEL) ?? DEFAULT_MODEL,
    profilePath: readEnvironmentValue(environment.SYSTEM_ONE_PROFILE) ?? defaultProfilePath(),
    timeoutMs: readTimeoutMs(environment.SYSTEM_ONE_TIMEOUT_MS),
    tracePath: readEnvironmentValue(environment.SYSTEM_ONE_TRACE_PATH) ?? defaultTracePath(),
    imageDirectory: readEnvironmentValue(environment.SYSTEM_ONE_IMAGE_DIR) ??
      defaultImageDirectory(),
  };
}

const configuration = readConfiguration(process.env);

// Composition root: one evaluation operation around the real adapters. It holds no
// connection state, so the server factory below may build a fresh MCP surface per
// connection while sharing this instance.
const evaluateOddEvidence = new EvaluateOddEvidence({
  decisionGateway: new LmStudioDecisionGateway({
    endpoint: configuration.endpoint,
    model: configuration.model,
    timeoutMs: configuration.timeoutMs,
  }),
  questionProfileSource: new ProfileFileSource({ profilePath: configuration.profilePath }),
  tracing: {
    evaluationTrace: new JsonLinesEvaluationTrace({ tracePath: configuration.tracePath }),
    imageStore: new ImageStore({ directory: configuration.imageDirectory }),
    // The gateway is built with this same configured model, so the recorded request
    // carries the value the wire body carries.
    decisionModel: configuration.model,
  },
});

const serverOptions: OddEvidenceServerOptions = {
  expectedModel: configuration.model,
  profilePath: configuration.profilePath,
};

// The installed SDK's stdio entry owns the connection: it decides the protocol era from
// the opening exchange, pins exactly one instance from this factory for the connection
// lifetime, and closes the transport when stdin ends. A hand-wired
// `server.connect(new StdioServerTransport())` would leave that era decision and the
// per-era instance lifecycle to this module for no benefit.
serveStdio(() => createOddEvidenceServer({ evaluateOddEvidence }, serverOptions), {
  // Out-of-band transport errors are diagnostics, so they reach stderr and never stdout.
  onerror: (error) => {
    process.stderr.write(`system-one-mcp: ${error.name}: ${error.message}\n`);
  },
});

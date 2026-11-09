// Test data and doubles for the portable MCP surface: a contract-valid tool input
// carrying one inline image, inputs that exceed the advertised image-count and base64
// bounds, a validated evaluation result, and a recording evaluator double that returns
// it. Every creator returns fresh values; no module-level mutable state is shared.

import type { OddEvidenceEvaluation } from '../../application/evaluate-odd-evidence.ts';
import type { DecisionChoice, ValidatedDecisionAnswer } from '../../domain/decision-response.ts';
import type { OddEvidenceImage } from '../../domain/odd-evidence.ts';
import {
  MAX_ODD_EVIDENCE_IMAGE_BASE64_LENGTH,
  MAX_ODD_EVIDENCE_IMAGES,
  type OddEvidenceEvaluator,
  type OddEvidenceServerOptions,
} from '../../mcp/odd-evidence-server.ts';
import { createExpectedModel } from './odd-evidence.factory.ts';

export type EvaluateToolInput = {
  readonly text: string;
  readonly images: ReadonlyArray<OddEvidenceImage>;
};

const evidenceText = 'The latest user request repeats the accepted implementation scope.';

export function createEvaluateToolImage(): OddEvidenceImage {
  return {
    mimeType: 'image/png',
    base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  };
}

export function createEvaluateToolInput(
  image: OddEvidenceImage = createEvaluateToolImage(),
): EvaluateToolInput {
  return { text: evidenceText, images: [image] };
}

// One image beyond the advertised limit; the request must be rejected before the
// evaluation operation is asked to decide anything.
export function createOverLimitImagesToolInput(): EvaluateToolInput {
  return {
    text: evidenceText,
    images: Array.from({ length: MAX_ODD_EVIDENCE_IMAGES + 1 }, createEvaluateToolImage),
  };
}

// One base64 character beyond the advertised length.
export function createOverLengthBase64ToolInput(): EvaluateToolInput {
  return createEvaluateToolInput({
    mimeType: 'image/png',
    base64: 'A'.repeat(MAX_ODD_EVIDENCE_IMAGE_BASE64_LENGTH + 1),
  });
}

// A contract-valid evaluation result carrying the three answer IDs the delivered payload
// keeps: the two asked questions plus the derived visual_evidence answer.
export function createEvaluationResult(): OddEvidenceEvaluation {
  return {
    ok: true,
    profileId: 'odd-evidence-v1',
    profileVersion: 1,
    answers: {
      scope_changed: createValidatedAnswer('present'),
      user_only_decision: createValidatedAnswer('absent'),
      visual_evidence: createValidatedAnswer('absent'),
    },
  };
}

export function createServerOptions(): OddEvidenceServerOptions {
  return {
    expectedModel: createExpectedModel(),
    profilePath: '.opencode/plugins/odd-adviser/questions/odd-evidence-v1.json',
  };
}

// The evaluator double records every call it receives, so a test can assert whether the
// supplied evidence reached the operation and how often. Each creator returns a fresh
// instance with its own call log; the `calls` getter returns a snapshot copy.
export type RecordedEvaluationCall = {
  readonly text: string;
  readonly images: ReadonlyArray<OddEvidenceImage>;
  readonly expectedModel: string;
};

export type RecordingOddEvidenceEvaluator = OddEvidenceEvaluator & {
  readonly calls: ReadonlyArray<RecordedEvaluationCall>;
};

export function createRecordingEvaluateOddEvidence(
  result: OddEvidenceEvaluation = createEvaluationResult(),
): RecordingOddEvidenceEvaluator {
  const calls: RecordedEvaluationCall[] = [];
  return {
    execute: async (
      text: string,
      images: ReadonlyArray<OddEvidenceImage>,
      expectedModel: string,
    ) => {
      calls.push({ text, images: images.map((image) => ({ ...image })), expectedModel });
      return result;
    },
    get calls() {
      return calls.slice();
    },
  };
}

function createValidatedAnswer(choice: DecisionChoice): ValidatedDecisionAnswer {
  const probabilities: Record<DecisionChoice, number> = {
    present: 0.1,
    absent: 0.1,
  };
  probabilities[choice] = 0.8;
  return { type: 'choice', choice, probabilities, confidence: 0.8 };
}

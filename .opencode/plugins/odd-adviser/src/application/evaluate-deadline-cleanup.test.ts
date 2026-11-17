import { describe, expect, test } from "vitest";
import { EvaluateEvidence } from "./evaluate-evidence.ts";
import {
	createCapturedMessage,
	createControlledDeadline,
	createEvaluateEvidenceOptions,
	createEvaluation,
	createExpectedEvaluatedAdvisory,
	createExpectedUnavailableAdvisory,
	createRecordingEvaluator,
	createThrowingEvaluator,
} from "#test/helpers/plugin.factory.ts";

describe("evaluateEvidence deadline cleanup", () => {
	test("cancels the pending deadline when evaluation succeeds first", async () => {
		const deadline = createControlledDeadline();
		const evaluation = createEvaluation();
		const outcome = await new EvaluateEvidence({
			evaluator: createRecordingEvaluator(evaluation),
			deadline,
		}).execute(createCapturedMessage(), createEvaluateEvidenceOptions());

		expect(outcome).toStrictEqual(createExpectedEvaluatedAdvisory(evaluation, expect.any(String)));
		expect(deadline.cancellations).toBe(1);
		expect(deadline.isPending).toBe(false);
	});

	test("cancels the pending deadline when evaluation rejects first", async () => {
		const deadline = createControlledDeadline();
		const outcome = await new EvaluateEvidence({
			evaluator: createThrowingEvaluator(),
			deadline,
		}).execute(createCapturedMessage(), createEvaluateEvidenceOptions());

		expect(outcome).toStrictEqual(createExpectedUnavailableAdvisory("transport_error", expect.any(String)));
		expect(deadline.cancellations).toBe(1);
		expect(deadline.isPending).toBe(false);
	});
});

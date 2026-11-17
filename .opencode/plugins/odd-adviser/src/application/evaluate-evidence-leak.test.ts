import { describe, expect, test } from "vitest";
import { EvaluateEvidence } from "./evaluate-evidence.ts";
import { formatAdvisoryBlock } from "#domain/advisory-block.ts";
import {
	createControlledDeadline,
	createEvaluateEvidenceOptions,
	createExpectedUnavailableAdvisory,
	createLeakCanary,
	createRecordingEvaluator,
	createUnavailableEvaluator,
	type LeakCanary,
} from "#test/helpers/plugin.factory.ts";

function expectNoEvidenceLeak(advisory: string, canary: LeakCanary): void {
	expect(advisory.length).toBeGreaterThan(0);
	for (const fragment of canary.forbiddenFragments) expect(advisory).not.toContain(fragment);
}

describe("evaluateEvidence evidence confidentiality", () => {
	test("delivers an evaluated advisory and the block built from it that repeat no supplied text or image bytes", async () => {
		const canary = createLeakCanary();
		const outcome = await new EvaluateEvidence({
			evaluator: createRecordingEvaluator(),
			deadline: createControlledDeadline(),
		}).execute(canary.message, createEvaluateEvidenceOptions());
		expect(outcome.status).toBe("evaluated");
		expectNoEvidenceLeak(outcome.advisory, canary);
		expectNoEvidenceLeak(formatAdvisoryBlock(outcome), canary);
	});

	test("delivers an unavailable advisory that repeats no supplied text or image bytes", async () => {
		const canary = createLeakCanary();
		const outcome = await new EvaluateEvidence({
			evaluator: createUnavailableEvaluator(),
			deadline: createControlledDeadline(),
		}).execute(canary.message, createEvaluateEvidenceOptions());
		expect(outcome).toStrictEqual(createExpectedUnavailableAdvisory("tool_error", expect.any(String)));
		expectNoEvidenceLeak(outcome.advisory, canary);
	});
});

// Unit test of the decision-response contract at its approved boundary. The rule that a
// model decision response is accepted or rejected is owned by the evaluation operation:
// `EvaluateOddEvidence.execute()` validates the body its decision-gateway port returns.
// Each case therefore drives the real operation with that port doubled to return the
// specific response body, and observes the delivered rejection code — the same rule,
// exercised through the approved unit target rather than the pure validator directly.

import { expect, test } from "vitest";

import { EvaluateOddEvidence } from "#application/evaluate-odd-evidence.ts";
import {
	createDecisionResponse,
	createDecisionResponseWithInvalidProbability,
	createDecisionResponseWithModelMismatch,
	createDecisionResponseWithThirdProbabilityState,
	createDecisionResponseWithUnknownChoice,
} from "#test/decision-response.factory.ts";
import {
	createDecisionGateway,
	createEvidence,
	createExpectedModel,
	createQuestionProfileSource,
} from "#test/odd-evidence.factory.ts";

// One evaluation whose decision gateway returns the supplied response body. The profile
// and evidence are contract-valid, so the only variable is the response under test.
async function evaluateReturnedResponse(response: unknown) {
	const evidence = createEvidence();
	const operation = new EvaluateOddEvidence({
		decisionGateway: createDecisionGateway(response),
		questionProfileSource: createQuestionProfileSource(),
	});
	return operation.execute(evidence.text, evidence.images, createExpectedModel());
}

test("accepts a response answering exactly present and absent", async () => {
	const response = createDecisionResponse();
	const result = await evaluateReturnedResponse(response);

	expect(result.ok).toBe(true);
	if (!result.ok) return;
	// The accepted model answers are delivered unchanged for the two questions the profile
	// asks; the derived visual_evidence answer is appended by the operation, not the model.
	expect(result.answers.scope_changed).toStrictEqual(response.answers.scope_changed);
	expect(result.answers.user_only_decision).toStrictEqual(response.answers.user_only_decision);
	// The accepted answer carries exactly the two declared states and no third one.
	for (const questionId of ["scope_changed", "user_only_decision"] as const) {
		expect(Object.keys(result.answers[questionId].probabilities).sort()).toStrictEqual(["absent", "present"]);
	}
});

test("rejects a response choosing the removed third state", async () => {
	const result = await evaluateReturnedResponse(createDecisionResponseWithUnknownChoice());

	expect(result.ok).toBe(false);
	if (result.ok) return;
	// The rejection is the choice rule itself, not a probability defect in the fixture.
	expect(result.code).toBe("invalid_answer");
});

test("rejects an answer carrying a third probability state", async () => {
	const result = await evaluateReturnedResponse(createDecisionResponseWithThirdProbabilityState());

	expect(result.ok).toBe(false);
	if (result.ok) return;
	// The extra state is rejected by the probability rule, so a profile's two declared
	// states are also the only states a response may score.
	expect(result.code).toBe("invalid_probabilities");
});

test("rejects a response with an invalid probability", async () => {
	const result = await evaluateReturnedResponse(createDecisionResponseWithInvalidProbability());

	expect(result.ok).toBe(false);
});

test("rejects a response from the wrong model", async () => {
	const result = await evaluateReturnedResponse(createDecisionResponseWithModelMismatch());

	expect(result.ok).toBe(false);
});

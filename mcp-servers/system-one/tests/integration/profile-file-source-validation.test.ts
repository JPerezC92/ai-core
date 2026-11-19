// Integration test of the question-profile loader across its filesystem boundary. The
// domain validator is the loader adapter's single mapping step — `ProfileFileSource.load()`
// reads, parses and validates the document in one step — so its accepted and rejected
// shapes are exercised here, at the boundary that owns that mapping. Each document shape
// is written as a real temporary JSON file and read back through the real adapter.

import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { expect, test } from "vitest";

import { ProfileFileSource } from "#infrastructure/profile-file-source.ts";
import {
	createQuestionProfile,
	createQuestionProfileWithDerivedQuestion,
	createQuestionProfileWithMalformedQuestion,
	createQuestionProfileWithNonChoiceQuestion,
	createQuestionProfileWithoutProfileId,
	createQuestionProfileWithThirdCriterionState,
} from "#test/question-profile.factory.ts";

// One real file per document shape: the adapter reads it, parses it and validates it, so
// the accept or reject outcome is the loader's own, not the validator's return applied to
// an in-memory value. The temporary file is removed once its value is materialized, so
// each case is independent of every other case.
async function loadDocument(document: unknown) {
	const directory = await mkdtemp(join(tmpdir(), "system-one-profile-"));
	try {
		const profilePath = join(directory, "profile.json");
		await writeFile(profilePath, JSON.stringify(document), "utf8");
		return await new ProfileFileSource({ profilePath }).load();
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}

test("accepts a profile declaring exactly present and absent for both questions", async () => {
	const document = createQuestionProfile();
	const loaded = await loadDocument(document);

	if (!loaded.ok) {
		throw new Error(`the valid profile must load: ${loaded.reason}`);
	}
	expect(loaded.profile).toStrictEqual(document);
	// The accepted profile declares exactly the two reachable states and no third one.
	for (const question of Object.values(loaded.profile.questions)) {
		expect(Object.keys(question.criteria).sort()).toStrictEqual(["absent", "present"]);
	}
});

test("rejects a profile that asks the derived visual evidence question", async () => {
	const loaded = await loadDocument(createQuestionProfileWithDerivedQuestion());

	// The model is asked exactly two questions; the visual_evidence answer is derived from
	// the supplied images. The rejection is for the extra question itself, not for an
	// unrelated defect: the same profile without it is accepted by the case above.
	expect(loaded).toStrictEqual({
		ok: false,
		reason: "Invalid question profile metadata or question IDs",
	});
});

test("rejects a profile declaring a third criterion state", async () => {
	const loaded = await loadDocument(createQuestionProfileWithThirdCriterionState());

	// The rejection is for the extra state itself, not for an unrelated defect: the same
	// profile without it is accepted by the case above.
	expect(loaded).toStrictEqual({
		ok: false,
		reason: "Invalid question: scope_changed",
	});
});

test("rejects a non-choice question", async () => {
	const loaded = await loadDocument(createQuestionProfileWithNonChoiceQuestion());

	expect(loaded.ok).toBe(false);
});

test("rejects a profile without an identifier", async () => {
	const loaded = await loadDocument(createQuestionProfileWithoutProfileId());

	expect(loaded.ok).toBe(false);
});

test("rejects an additional malformed question", async () => {
	const loaded = await loadDocument(createQuestionProfileWithMalformedQuestion());

	expect(loaded.ok).toBe(false);
});

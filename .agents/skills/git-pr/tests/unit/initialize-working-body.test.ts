import { describe, expect, it, vi } from "vitest";

import { InitializeWorkingBody } from "#scripts/pr_content/application/initialize_working_body.ts";
import {
	makeCreationBody,
	makeCreationDraft,
	makeInitializePaths,
	makeMalformedDraft,
} from "#tests/support/review-content-fixtures.ts";

describe("working body initialization", () => {
	it("creates the supplied path with the exact extracted body", () => {
		const read = vi.fn((_path: string): string => makeCreationDraft());
		const create = vi.fn();
		const paths = makeInitializePaths();

		const outcome = new InitializeWorkingBody(read, create).execute(paths);

		expect(outcome).toEqual({ body: makeCreationBody() });
		expect(create).toHaveBeenCalledExactlyOnceWith(paths.workingBodyPath, makeCreationBody());
	});

	it("reads the supplied draft path", () => {
		const read = vi.fn((_path: string): string => makeCreationDraft());
		const paths = makeInitializePaths({ draftPath: "/tmp/supplied-draft.md" });

		new InitializeWorkingBody(read, vi.fn()).execute(paths);

		expect(read).toHaveBeenCalledExactlyOnceWith(paths.draftPath);
	});

	it("returns the extraction refusal and creates nothing for a malformed draft", () => {
		const read = vi.fn((_path: string): string => makeMalformedDraft());
		const create = vi.fn();

		const outcome = new InitializeWorkingBody(read, create).execute(makeInitializePaths());

		expect("code" in outcome ? outcome.code : "").toBe("DRAFT_INVALID");
		expect(create).not.toHaveBeenCalled();
	});

	it("refuses a draft the canonical findings parser rejects and creates nothing", () => {
		const draft = makeCreationDraft(
			[
				"## Summary",
				"",
				"- Adds the review preparation commands.",
				"",
				"## Test plan",
				"",
				"- [ ] Run the focused suite",
				"- [ ] Confirm the import map resolves",
				"",
				"## Findings / blockers",
				"",
				"No review findings yet.",
				"",
				"Explanatory prose the canonical parser rejects.",
				"",
			].join("\n"),
		);
		const create = vi.fn();

		const outcome = new InitializeWorkingBody(
			vi.fn(() => draft),
			create,
		).execute(makeInitializePaths());

		expect("code" in outcome ? outcome.code : "").toBe("DRAFT_INVALID");
		expect(create).not.toHaveBeenCalled();
	});

	it("refuses a draft whose test plan has fewer than two items", () => {
		const draft = makeCreationDraft(makeCreationBody({ items: ["Only one item"] }));
		const create = vi.fn();

		const outcome = new InitializeWorkingBody(
			vi.fn(() => draft),
			create,
		).execute(makeInitializePaths());

		expect("code" in outcome ? outcome.code : "").toBe("DRAFT_INVALID");
		expect(create).not.toHaveBeenCalled();
	});

	it("refuses a draft whose plan carries an item the final validator would reject", () => {
		const body = makeCreationBody({
			items: ["Run the focused suite", "Confirm the import map resolves", "Re-run the focused suite"],
		}).replace("- [ ] Confirm the import map resolves", "- [x] Confirm the import map resolves");
		const create = vi.fn();

		const outcome = new InitializeWorkingBody(
			vi.fn(() => makeCreationDraft(body)),
			create,
		).execute(makeInitializePaths());

		expect("code" in outcome ? outcome.code : "").toBe("DRAFT_INVALID");
		expect(create).not.toHaveBeenCalled();
	});

	it("refuses a draft whose plan repeats an item the final validator would reject", () => {
		const body = makeCreationBody({ items: ["Run the focused suite", "Run the focused suite"] });
		const create = vi.fn();

		const outcome = new InitializeWorkingBody(
			vi.fn(() => makeCreationDraft(body)),
			create,
		).execute(makeInitializePaths());

		expect("code" in outcome ? outcome.code : "").toBe("DRAFT_INVALID");
		expect(create).not.toHaveBeenCalled();
	});

	it("refuses a draft that carries a review verdict line", () => {
		const body = `${makeCreationBody()}\n[PASS] — 0 open findings\n`;
		const create = vi.fn();

		const outcome = new InitializeWorkingBody(
			vi.fn(() => makeCreationDraft(body)),
			create,
		).execute(makeInitializePaths());

		expect("code" in outcome ? outcome.code : "").toBe("DRAFT_INVALID");
		expect(create).not.toHaveBeenCalled();
	});

	it("propagates a reader failure as an exception", () => {
		const failure = new Error("ENOENT: no such file or directory");
		const read = vi.fn((_path: string): string => {
			throw failure;
		});

		expect(() => new InitializeWorkingBody(read, vi.fn()).execute(makeInitializePaths())).toThrow(failure);
	});

	it("propagates a creation failure as an exception", () => {
		const failure = new Error("EEXIST: file already exists");
		const read = vi.fn((_path: string): string => makeCreationDraft());
		const create = vi.fn((_path: string, _content: string): void => {
			throw failure;
		});

		expect(() => new InitializeWorkingBody(read, create).execute(makeInitializePaths())).toThrow(failure);
	});
});

import { describe, expect, it, vi } from "vitest";

import { InitializeWorkingBody } from "#scripts/pr_content/application/initialize_working_body.ts";
import {
	makeCompletedBody,
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

		expect(outcome).toEqual({ body: makeCompletedBody() });
		expect(create).toHaveBeenCalledExactlyOnceWith(paths.workingBodyPath, makeCompletedBody());
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

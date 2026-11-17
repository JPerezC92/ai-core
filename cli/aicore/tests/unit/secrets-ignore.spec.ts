/**
 * Unit: the destination Git ignore rule for `.secrets/`.
 *
 * One behavioral concern — an absent ignore file becomes a single-rule file;
 * an effective `.secrets` or `.secrets/` path rule is left alone; a commented
 * line does not count; any other present file keeps its bytes and gains the
 * rule on a new line.
 */

import { describe, expect, test } from "vitest";

import { withSecretsIgnore } from "#domain/synchronization/secrets-ignore.ts";

describe("withSecretsIgnore", () => {
	test("an absent file becomes a single-rule ignore file", () => {
		expect(withSecretsIgnore(null)).toBe(".secrets/\n");
	});

	test("an effective .secrets/ rule is left unchanged", () => {
		const existing = "node_modules/\n.secrets/\n";
		expect(withSecretsIgnore(existing)).toBe(existing);
	});

	test("an effective .secrets rule with a trailing comment counts", () => {
		const existing = ".secrets # local credentials\n";
		expect(withSecretsIgnore(existing)).toBe(existing);
	});

	test("a commented-out line does not count", () => {
		expect(withSecretsIgnore("# .secrets/\n")).toBe("# .secrets/\n.secrets/\n");
	});

	test("other rules are preserved, including a missing trailing newline", () => {
		expect(withSecretsIgnore("dist")).toBe("dist\n.secrets/\n");
	});
});

import { describe, expect, it } from "vitest";

import { CLEARANCE_SCHEMA } from "#domain/synchronization/constants.ts";
import { parseClearanceDocument } from "#domain/synchronization/clearance.ts";

// A record whose only defect is the role value, so the assertion reads the message that
// renders that value. Region mode keeps the record valid in every other respect.
function documentWithRole(role: unknown): unknown {
	return { schema: CLEARANCE_SCHEMA, cleared: { "docs/a.md": { mode: "region", role } } };
}

function reasonFor(role: unknown): string {
	const parsed = parseClearanceDocument(documentWithRole(role));
	expect(parsed.ok).toBe(false);
	return parsed.ok ? "" : parsed.reason;
}

describe("clearance invalid role diagnostic", () => {
	it("renders a primitive role exactly as before", () => {
		expect(reasonFor("owner")).toBe("cleared record for docs/a.md has an invalid role: owner");
		expect(reasonFor(7)).toBe("cleared record for docs/a.md has an invalid role: 7");
		expect(reasonFor(false)).toBe("cleared record for docs/a.md has an invalid role: false");
		expect(reasonFor(null)).toBe("cleared record for docs/a.md has an invalid role: null");
	});

	it("renders a mapping role as JSON instead of collapsing it", () => {
		expect(reasonFor({ nested: "value" })).toBe(
			'cleared record for docs/a.md has an invalid role: {"nested":"value"}',
		);
	});

	it("renders a list role as JSON instead of joining its members", () => {
		expect(reasonFor(["a", "b"])).toBe('cleared record for docs/a.md has an invalid role: ["a","b"]');
		expect(reasonFor([1, 2])).toBe("cleared record for docs/a.md has an invalid role: [1,2]");
	});
});

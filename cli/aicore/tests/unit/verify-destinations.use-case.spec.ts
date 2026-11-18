/**
 * Unit: the verification use case's currency judgement, with its ports doubled.
 *
 * One behavioral concern, one group per verdict: a bound source whose clearance
 * record now declares another destination is drift naming the source and both
 * destinations, before the reconciliation blocker is synced and before any
 * destination payload is read, so a diverged binding is never called current and
 * nothing is written (contract T2, T3; `check`'s only write is the blocker).
 *
 * A region destination is then judged by its core region and its frontmatter, not
 * by its project region; a merge destination is current when the destination
 * holds every source key; a stale pinned revision and an unreadable document are
 * refused with their own failure class; and a pending path whose source is no
 * longer region-bound is reported rather than reconciled.
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { VerifyDestinations } from "#application/synchronization/verify-destinations.ts";
import type {
	BindingsStore,
	ClearanceStore,
	DestinationFiles,
	FilesystemLayout,
	SourceFiles,
	WriteTargetGuard,
} from "#domain/synchronization/ports.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import { OTHER_REVISION } from "#support/aicore-cli.factory.ts";
import {
	BOUND_SOURCE,
	RELOCATED_BOUND_DESTINATION,
	makeBindingsDocument,
	makeClearanceLoad,
	makeRelocatedClearanceLoad,
	makeSynchronizationRequest,
} from "#support/synchronization.factory.ts";

/** The verification use case, its ports doubled and arranged for one run. */
function makeVerification(options: { readonly clearance: MockProxy<ClearanceStore> }): {
	readonly useCase: VerifyDestinations;
	readonly bindings: MockProxy<BindingsStore>;
	readonly sources: MockProxy<SourceFiles>;
	readonly destinations: MockProxy<DestinationFiles>;
	readonly layout: MockProxy<FilesystemLayout>;
} {
	const bindings = mock<BindingsStore>();
	bindings.load.mockResolvedValue(makeBindingsDocument());
	const guard = mock<WriteTargetGuard>();
	guard.refuse.mockResolvedValue(null);
	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	const sources = mock<SourceFiles>();
	const destinations = mock<DestinationFiles>();
	const useCase = new VerifyDestinations({
		bindings,
		clearance: options.clearance,
		sources,
		destinations,
		layout,
		guard,
	});
	return { useCase, bindings, sources, destinations, layout };
}

describe("destination drift refusal", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a source the registry relocated is refused by name and nothing is written", async () => {
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeRelocatedClearanceLoad());
		const { useCase, bindings, sources, destinations, layout } = makeVerification({ clearance });

		const outcome = await useCase.execute(makeSynchronizationRequest());

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		// The report names the source, the destination it is bound to, and the one
		// the registry now declares.
		expect(failure?.message).toContain(`destination drift: ${BOUND_SOURCE} is bound to '${BOUND_SOURCE}'`);
		expect(failure?.message).toContain(`now declares '${RELOCATED_BOUND_DESTINATION}'`);

		// Nothing was written and no payload was read from a destination, so the
		// divergence cannot be masked by a blocker sync or a currency report.
		expect(bindings.save).not.toHaveBeenCalled();
		expect(bindings.writeReport).not.toHaveBeenCalled();
		expect(destinations.readText).not.toHaveBeenCalled();
		expect(destinations.readBytes).not.toHaveBeenCalled();
		expect(layout.syncBlocker).not.toHaveBeenCalled();
		expect(sources.readCore).not.toHaveBeenCalled();
	});
});

/** The merge-mode source: the harness configuration. */
const CONFIGURED_SOURCE = ".opencode/opencode.jsonc";

/** The shipped configuration's `mcp` block, as the source carries it. */
const CONFIGURED_TEXT = `{
  "mcp": {
    "servers": {
      "system-one": { "type": "local", "command": ["node", "mcp-servers/system-one/src/mcp/stdio.ts"] },
      "qmd": { "type": "local", "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "ai-core", "mcp"] }
    }
  }
}`;

/** The merged configuration a destination that never received the omitted server holds. */
const MERGED_TEXT = `{
      "mcp": {
        "servers": {
          "qmd": { "type": "local", "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "destination", "mcp"] }
        }
      }
    }`;

/** The verification operation over one merge-mode binding and a stated registry. */
function makeMergeVerification(options: { readonly omitSystemOne: boolean }): {
	readonly useCase: VerifyDestinations;
	readonly sources: MockProxy<SourceFiles>;
	readonly destinations: MockProxy<DestinationFiles>;
} {
	const bindings = mock<BindingsStore>();
	bindings.load.mockResolvedValue(
		makeBindingsDocument({
			editor: "opencode",
			bindings: [{ source: CONFIGURED_SOURCE, destinations: [CONFIGURED_SOURCE], declaredMode: "merge" }],
		}),
	);

	const clearance = mock<ClearanceStore>();
	clearance.load.mockResolvedValue(
		makeClearanceLoad({
			[CONFIGURED_SOURCE]: {
				mode: "merge",
				...(options.omitSystemOne ? { omit_mcp_servers: ["system-one"] } : {}),
			},
		}),
	);

	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	layout.isFile.mockResolvedValue(true);
	layout.exists.mockResolvedValue(true);

	const guard = mock<WriteTargetGuard>();
	guard.refuse.mockResolvedValue(null);

	const sources = mock<SourceFiles>();
	sources.readText.mockResolvedValue(CONFIGURED_TEXT);

	const destinations = mock<DestinationFiles>();
	destinations.readText.mockResolvedValue(MERGED_TEXT);

	const useCase = new VerifyDestinations({ bindings, clearance, sources, destinations, layout, guard });
	return { useCase, sources, destinations };
}

describe("merge currency", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("check stays current when the destination never received the omitted server", async () => {
		const { useCase } = makeMergeVerification({ omitSystemOne: true });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.message).toBe("current");
	});

	test("without the omission the same destination is merge drift", async () => {
		const { useCase } = makeMergeVerification({ omitSystemOne: false });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toBe(`merge drift: G:/projects/destination/${CONFIGURED_SOURCE}`);
	});
});

/** The region-mode source's own frontmatter, which a write refreshes into the destination. */
const REGION_SOURCE_TEXT = "---\nversion: 2.0.0\n---\n";

/** The region-mode source's core bytes, as its reader reports them. */
const REGION_CORE = "core body\n";

/** A destination marked document carrying `core` inside its core region. */
function marked(core: string, project: string, frontmatter = ""): string {
	return (
		frontmatter +
		`<!-- core:begin -->\n${core}<!-- core:end -->\n\n` +
		`<!-- project:begin -->\n${project}<!-- project:end -->\n`
	);
}

type RegionArrangement = {
	/** The bindings store's load result; `null` reports a malformed document. */
	readonly document?: BindingsDocument | null;
	/** The clearance registry's cleared records. */
	readonly clearance?: Readonly<Record<string, Readonly<Record<string, unknown>>>>;
	/** The destination document's text, as its reader reports it. */
	readonly destinationContent?: string | null;
	readonly sourceCore?: string;
	readonly sourceText?: string;
};

/** The verification use case arranged over one bound source. */
function makeRegionVerification(options: RegionArrangement = {}) {
	const bindings = mock<BindingsStore>();
	bindings.load.mockResolvedValue(options.document === undefined ? makeBindingsDocument() : options.document);

	const clearance = mock<ClearanceStore>();
	clearance.load.mockResolvedValue(makeClearanceLoad(options.clearance ?? { [BOUND_SOURCE]: { mode: "region" } }));

	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	layout.isFile.mockResolvedValue(true);
	layout.exists.mockResolvedValue(true);

	const guard = mock<WriteTargetGuard>();
	guard.refuse.mockResolvedValue(null);

	const sources = mock<SourceFiles>();
	sources.readCore.mockResolvedValue({ kind: "core", core: options.sourceCore ?? REGION_CORE });
	sources.readText.mockResolvedValue(options.sourceText ?? REGION_SOURCE_TEXT);

	const destinations = mock<DestinationFiles>();
	destinations.readText.mockResolvedValue(
		options.destinationContent === undefined ? marked(REGION_CORE, "") : options.destinationContent,
	);

	const useCase = new VerifyDestinations({ bindings, clearance, sources, destinations, layout, guard });
	return { useCase, bindings, layout, sources, destinations };
}

describe("region currency", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a destination whose core region matches the source is current, whatever its project region holds", async () => {
		const { useCase } = makeRegionVerification({
			// The project region is the destination's own: editing it never makes the
			// destination drift, because no write would change it.
			destinationContent: marked(REGION_CORE, "this project's own rules\n"),
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.message).toBe("current");
	});

	test("a core region that no longer matches the source is region drift", async () => {
		const { useCase } = makeRegionVerification({
			destinationContent: marked("superseded core\n", ""),
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toBe(`region drift: G:/projects/destination/${BOUND_SOURCE}`);
	});

	test("a frontmatter a write would change is frontmatter drift, distinct from a region difference", async () => {
		const { useCase } = makeRegionVerification({
			// The core region already matches; only the frontmatter is stale.
			destinationContent: marked(REGION_CORE, "", "---\nversion: 1.0.0\n---\n"),
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toBe(`frontmatter drift: G:/projects/destination/${BOUND_SOURCE}`);
	});
});

describe("revision and input refusals", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a pinned revision that does not match the source is revision drift", async () => {
		const { useCase } = makeRegionVerification({
			document: makeBindingsDocument({ coreRevision: OTHER_REVISION }),
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toBe("revision drift: bindings revision does not match source");
	});

	test("an unreadable bindings document is refused as malformed input", async () => {
		const { useCase, layout } = makeRegionVerification({ document: null });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toContain("invalid bindings:");
		// The blocker is not synced for a document that could not be read.
		expect(layout.syncBlocker).not.toHaveBeenCalled();
	});

	test("a pending path whose source is raw-bound is reported by check", async () => {
		const { useCase } = makeRegionVerification({
			document: makeBindingsDocument({
				bindings: [{ source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "raw" }],
				pending: [BOUND_SOURCE],
			}),
			clearance: { [BOUND_SOURCE]: { mode: "raw" } },
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toContain("stale raw-bound pending paths cannot be reconciled");
		expect(failure?.message).toContain(BOUND_SOURCE);
	});

	test("a destination core marker pair that is missing, reversed or duplicated is malformed", async () => {
		const brokenDocuments = [
			"# A destination that carries no core marker pair at all.\n",
			`<!-- core:end -->\nshared\n<!-- core:begin -->\n`,
			`<!-- core:begin -->\nshared\n<!-- core:end -->\n<!-- core:begin -->\nagain\n<!-- core:end -->\n`,
		];

		for (const destinationContent of brokenDocuments) {
			const { useCase } = makeRegionVerification({ destinationContent });
			const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));
			expect(outcome.ok, destinationContent).toBe(false);
			const failure = outcome.ok ? null : outcome.failure;
			expect(failure?.code).toBe("invalid");
			expect(failure?.message).toContain("invalid destination markers");
		}
	});

	test("an unreadable source is drift and nothing is written", async () => {
		const { useCase, sources, layout } = makeRegionVerification();
		sources.readText.mockResolvedValue(null);
		sources.readCore.mockResolvedValue(null);

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toContain("missing source");
		expect(layout.syncBlocker).not.toHaveBeenCalled();
	});

	test("an absent raw-bound destination is drift and nothing is written", async () => {
		const { useCase, destinations } = makeRegionVerification({
			document: makeBindingsDocument({
				bindings: [{ source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "raw" }],
			}),
			clearance: { [BOUND_SOURCE]: { mode: "raw" } },
		});
		destinations.readText.mockResolvedValue(null);
		destinations.readBytes.mockResolvedValue(null);

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toContain("missing destination");
	});
});

/**
 * Unit: the destination-drift refusal at the verification use case.
 *
 * One behavioral concern — a bound source whose clearance record now declares
 * another destination is reported as drift naming the source and both
 * destinations, before the reconciliation blocker is synced and before any
 * destination payload is read, so a diverged binding is never called current and
 * nothing is written (contract T2, T3; `check`'s only write is the blocker).
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

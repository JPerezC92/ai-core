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
  makeRelocatedClearanceLoad,
  makeSynchronizationRequest,
} from "#support/synchronization.factory.ts";

/** The verification use case, its ports doubled and arranged for one run. */
function makeVerification(options: {
  readonly clearance: MockProxy<ClearanceStore>;
}): {
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
    expect(failure?.message).toContain(
      `destination drift: ${BOUND_SOURCE} is bound to '${BOUND_SOURCE}'`,
    );
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

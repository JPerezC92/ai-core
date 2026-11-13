/**
 * Unit: the destination-drift refusal at the enrollment use case.
 *
 * One behavioral concern — enrollment never moves a destination: an already-bound
 * source whose clearance record now declares another destination is the drift
 * `apply` and `check` refuse, reported by name before any destination is read,
 * recreated or rewritten, and before the bindings and their reconciliation report
 * are written (contract T2, T3).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { EnrollDestinations } from "#application/synchronization/enroll-destinations.ts";
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
  makeEnrollmentRequest,
  makeRelocatedClearanceLoad,
} from "#support/synchronization.factory.ts";

/** The enrollment use case, its ports doubled and arranged for one run. */
function makeEnrollment(options: {
  readonly clearance: MockProxy<ClearanceStore>;
}): {
  readonly useCase: EnrollDestinations;
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
  const useCase = new EnrollDestinations({
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
    const { useCase, bindings, sources, destinations, layout } = makeEnrollment({ clearance });

    const outcome = await useCase.execute(makeEnrollmentRequest());

    expect(outcome.ok).toBe(false);
    const failure = outcome.ok ? null : outcome.failure;
    expect(failure?.code).toBe("drift");
    // The report names the source, the destination it is bound to, and the one
    // the registry now declares.
    expect(failure?.message).toContain(
      `destination drift: ${BOUND_SOURCE} is bound to '${BOUND_SOURCE}'`,
    );
    expect(failure?.message).toContain(`now declares '${RELOCATED_BOUND_DESTINATION}'`);

    // Enrollment never moves a destination: no payload was read, no file was
    // created or rewritten, and no bindings or reconciliation report was saved.
    expect(bindings.save).not.toHaveBeenCalled();
    expect(bindings.writeReport).not.toHaveBeenCalled();
    expect(destinations.readText).not.toHaveBeenCalled();
    expect(destinations.readBytes).not.toHaveBeenCalled();
    expect(destinations.writeText).not.toHaveBeenCalled();
    expect(destinations.writeBytes).not.toHaveBeenCalled();
    expect(layout.syncBlocker).not.toHaveBeenCalled();
    expect(layout.ensureDirectory).not.toHaveBeenCalled();
    expect(sources.readCore).not.toHaveBeenCalled();
  });
});

/**
 * Unit: the update use case's refusals that stop a run before anything is
 * written.
 *
 * One behavioral concern, one group per refusal: the update use case reports a
 * typed returned failure — never an exception — that names what diverged, and no
 * destination payload is read, no binding is saved and no blocker is synced. A
 * run that asks for another editor than the destination is enrolled for never
 * reaches the write-target preflight; a source whose clearance record now
 * declares another destination is the destination drift `apply` refuses, naming
 * the source and both destinations (contract T2, T3).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
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

/** The update use case's doubled collaborators. */
type UpdatePorts = {
  readonly bindings: MockProxy<BindingsStore>;
  readonly clearance: MockProxy<ClearanceStore>;
  readonly sources: MockProxy<SourceFiles>;
  readonly destinations: MockProxy<DestinationFiles>;
  readonly layout: MockProxy<FilesystemLayout>;
  readonly guard: MockProxy<WriteTargetGuard>;
};

/** The update use case with every port doubled, overridable per case. */
function makeUpdate(
  overrides: Partial<UpdatePorts> = {},
): UpdatePorts & { readonly useCase: ApplyCoreRevision } {
  const bindings = overrides.bindings ?? mock<BindingsStore>();
  bindings.load.mockResolvedValue(makeBindingsDocument());
  const ports: UpdatePorts = {
    bindings,
    clearance: overrides.clearance ?? mock<ClearanceStore>(),
    sources: overrides.sources ?? mock<SourceFiles>(),
    destinations: overrides.destinations ?? mock<DestinationFiles>(),
    layout: overrides.layout ?? mock<FilesystemLayout>(),
    guard: overrides.guard ?? mock<WriteTargetGuard>(),
  };
  return { ...ports, useCase: new ApplyCoreRevision(ports) };
}

describe("enrolled-editor refusal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("a run for another editor is refused by name and never reaches the write-target guard", async () => {
    const { useCase, bindings, guard } = makeUpdate();

    const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "cursor" }));

    expect(outcome.ok).toBe(false);
    const failure = outcome.ok ? null : outcome.failure;
    expect(failure?.code).toBe("invalid");
    expect(failure?.message).toMatch(/enrolled for editor 'opencode'/);
    expect(failure?.message).toMatch(/requested 'cursor'/);

    // A refusal is reached before any write target is even classified.
    expect(guard.refuse).not.toHaveBeenCalled();
    expect(bindings.save).not.toHaveBeenCalled();
  });
});

describe("destination drift refusal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("a source the registry relocated is refused by name and nothing is written", async () => {
    const clearance = mock<ClearanceStore>();
    clearance.load.mockResolvedValue(makeRelocatedClearanceLoad());
    const layout = mock<FilesystemLayout>();
    layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
    const guard = mock<WriteTargetGuard>();
    guard.refuse.mockResolvedValue(null);
    const { useCase, bindings, sources, destinations } = makeUpdate({ clearance, layout, guard });

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

    // Nothing was written and no payload was read from a destination: the moved
    // destination is the destination owner's migration, not this run's.
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

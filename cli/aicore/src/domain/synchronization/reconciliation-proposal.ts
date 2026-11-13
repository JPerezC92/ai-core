/**
 * The reconciliation proposal's classification rule (pure).
 *
 * A proposal states, for every path a destination's bindings mention and every
 * file those bindings' destination directories hold, which class the path is in
 * and what a reconciliation would do about it. The rule is pure: it receives the
 * facts one inspection established — whether the registry still clears the
 * source, whether the source tree still holds it, whether the destination file
 * is present, and whether its content is still its source's — and returns the
 * class and the action.
 *
 * The ownership boundary is the point of the rule. A path whose ownership or
 * modifications cannot be established is *preserved* and reported, never
 * proposed for deletion: only a destination file whose bytes still equal the
 * source file standing at its path has proved it carries nothing of its own.
 * Everything a proposal states is a recommendation — the proposal itself writes
 * nothing, and performing it remains the destination owner's decision.
 */

import type { BindingMode } from "./constants.ts";

/** The four classes a path in the proposal falls into. */
export const PROPOSAL_CLASSES = [
  "managed",
  "superseded",
  "locally modified",
  "destination-owned",
] as const;

/** One class a path in the proposal falls into. */
export type ProposalClass = (typeof PROPOSAL_CLASSES)[number];

/** What a reconciliation would do about one path. */
export const PROPOSAL_ACTIONS = [
  "kept",
  "re-pointed",
  "moved",
  "deleted",
  "preserved",
] as const;

/** What a reconciliation would do about one path. */
export type ProposalAction = (typeof PROPOSAL_ACTIONS)[number];

/** The phrase every entry of unestablished ownership carries. */
export const OWNERSHIP_UNESTABLISHED = "ownership not established";

/** What one inspection established about one bound path. */
export type BoundPathObservation = {
  readonly source: string;
  readonly destination: string;
  /** The mode the registry clears this source under, or `null` when it clears none. */
  readonly mode: BindingMode | null;
  /** Where the registry delivers this source now; `null` when it clears none. */
  readonly declaredDestination: string | null;
  /** The source tree still holds the source path. */
  readonly sourcePresent: boolean;
  /** The destination holds the destination path. */
  readonly destinationPresent: boolean;
  /** The destination holds what its source declares, in its binding mode's sense. */
  readonly matchesSource: boolean;
  /** The destination file's bytes equal the source file's bytes. */
  readonly identical: boolean;
};

/** One line of the proposal. */
export type ProposalEntry = {
  /** The destination-relative path the line is about. */
  readonly path: string;
  /** The source it is bound to, or `null` when no binding names it. */
  readonly source: string | null;
  readonly classification: ProposalClass;
  readonly action: ProposalAction;
  /** Why this class and this action, in the operator's words. */
  readonly detail: string;
};

/** A destination's whole proposal. */
export type ReconciliationProposal = {
  readonly destination: string;
  readonly entries: readonly ProposalEntry[];
  /** Something in it needs the destination owner to decide or to act. */
  readonly requiresAction: boolean;
};

/**
 * Classify one bound path.
 *
 * A cleaned source that still exists and still lands where the bindings record
 * it is *managed*; a destination copy that no longer carries it is *locally
 * modified*. A cleaned source the registry now delivers elsewhere is still
 * managed, and the binding is *re-pointed* — the file itself is *moved* only
 * when its bytes are unchanged. Everything the registry no longer clears, or the
 * source tree no longer holds, is *superseded*, and is deleted only when the
 * source standing at its path still proves the destination copy unmodified.
 */
export function classifyBoundPath(observation: BoundPathObservation): ProposalEntry {
  const { source, destination } = observation;

  if (observation.mode !== null && observation.sourcePresent) {
    const declared = observation.declaredDestination ?? source;
    if (declared === destination) {
      return managedInPlace(observation, declared);
    }
    return managedElsewhere(observation, declared);
  }

  return superseded(observation);
}

/** A destination file no binding manages is the destination's own: kept. */
export function destinationOwnedEntry(path: string): ProposalEntry {
  return {
    path,
    source: null,
    classification: "destination-owned",
    action: "kept",
    detail: "no binding manages this path; it belongs to the destination",
  };
}

/** Report whether any entry needs the destination owner to decide or to act. */
export function proposalRequiresAction(entries: readonly ProposalEntry[]): boolean {
  return entries.some((entry) => entry.action !== "kept");
}

function managedInPlace(
  observation: BoundPathObservation,
  declared: string,
): ProposalEntry {
  if (!observation.destinationPresent) {
    return {
      path: observation.destination,
      source: observation.source,
      classification: "managed",
      action: "kept",
      detail: `absent from the destination; a synchronization creates it from ${declared}`,
    };
  }
  if (observation.matchesSource) {
    return {
      path: observation.destination,
      source: observation.source,
      classification: "managed",
      action: "kept",
      detail: `matches ${observation.source}`,
    };
  }
  return {
    path: observation.destination,
    source: observation.source,
    classification: "locally modified",
    action: "preserved",
    detail: `content differs from ${observation.source}; a synchronization would replace it, so the difference is the destination owner's to keep or to discard`,
  };
}

/**
 * A managed source the registry now delivers to another destination.
 *
 * The binding is re-pointed either way; whether the file itself travels depends
 * on whether it still carries exactly what its source holds.
 */
function managedElsewhere(
  observation: BoundPathObservation,
  declared: string,
): ProposalEntry {
  if (!observation.destinationPresent) {
    return {
      path: observation.destination,
      source: observation.source,
      classification: "managed",
      action: "re-pointed",
      detail: `the registry now delivers this source to ${declared}; the binding is re-pointed`,
    };
  }
  if (observation.identical) {
    return {
      path: observation.destination,
      source: observation.source,
      classification: "managed",
      action: "moved",
      detail: `its bytes are unchanged from ${observation.source}; move it to ${declared}`,
    };
  }
  return {
    path: observation.destination,
    source: observation.source,
    classification: "locally modified",
    action: "preserved",
    detail: `content differs from ${observation.source}; moving it would carry the difference to ${declared}, so it stays where it is`,
  };
}

/** A binding the registry no longer clears, or a source the tree no longer holds. */
function superseded(observation: BoundPathObservation): ProposalEntry {
  const cause =
    observation.mode === null && !observation.sourcePresent
      ? "no longer cleared for distribution and absent from the source tree"
      : observation.mode === null
        ? "no longer cleared for distribution"
        : "no longer present in the source tree";

  if (!observation.destinationPresent) {
    return {
      path: observation.destination,
      source: observation.source,
      classification: "superseded",
      action: "kept",
      detail: `${cause}; no destination file is present`,
    };
  }
  if (!observation.sourcePresent) {
    return {
      path: observation.destination,
      source: observation.source,
      classification: "superseded",
      action: "preserved",
      detail: `${OWNERSHIP_UNESTABLISHED} (${cause})`,
    };
  }
  if (observation.identical) {
    return {
      path: observation.destination,
      source: observation.source,
      classification: "superseded",
      action: "deleted",
      detail: `${cause}; its bytes are unchanged from ${observation.source}, so nothing of its own would be lost`,
    };
  }
  return {
    path: observation.destination,
    source: observation.source,
    classification: "superseded",
    action: "preserved",
    detail: `content differs from ${observation.source} (${cause}); the difference may be its own`,
  };
}

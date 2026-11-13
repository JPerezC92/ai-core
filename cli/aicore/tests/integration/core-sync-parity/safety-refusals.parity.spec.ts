/**
 * Integration: the negative safety cases of the behavioral-parity corpus.
 *
 * One behavioural concern — the refusals that protect the source tree and the
 * destination: unsafe write targets, aliased targets, overlapping roots,
 * malformed markers and clearance, and the drift classes.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("safety-refusals", "safety refusal parity");

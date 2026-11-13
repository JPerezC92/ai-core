/**
 * Integration: the raw-mode half of the behavioral-parity corpus.
 *
 * One behavioural concern — what a raw-mode binding produces: a byte-exact
 * copy, no ownership region, no reconciliation report and no pending entry.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("raw-mode", "raw mode parity");

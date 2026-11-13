/**
 * Integration: the bindings-schema half of the behavioral-parity corpus.
 *
 * One behavioural concern — the bindings document: how it is written, how a
 * malformed or unsafe one is rejected, and what happens to a pending entry
 * whose binding is no longer region-bound.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("bindings-schema", "bindings schema parity");

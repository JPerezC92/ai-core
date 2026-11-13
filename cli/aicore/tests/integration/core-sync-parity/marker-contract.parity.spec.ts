/**
 * Integration: the marker contract half of the behavioral-parity corpus.
 *
 * One behavioural concern — what counts as a marker: the markerless source,
 * the malformed marker pairs, the fenced marker literals and the untouched
 * project region.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("marker-contract", "marker contract parity");

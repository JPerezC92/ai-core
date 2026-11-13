/**
 * Integration: the exit-contract half of the behavioral-parity corpus.
 *
 * One behavioural concern — what each exit code means: 0 for a current or
 * applied result, 1 for drift and 2 for malformed input, with the observable
 * result of each.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("exit-contract", "exit contract parity");

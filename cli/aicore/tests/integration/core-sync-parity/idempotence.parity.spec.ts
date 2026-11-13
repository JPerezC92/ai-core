/**
 * Integration: the idempotence half of the behavioral-parity corpus.
 *
 * One behavioural concern — that applying or enrolling twice changes nothing
 * the second time.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("idempotence", "idempotence parity");

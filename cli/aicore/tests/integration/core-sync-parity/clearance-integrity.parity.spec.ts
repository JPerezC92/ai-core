/**
 * Integration: the clearance-registry integrity half of the behavioral-parity
 * corpus.
 *
 * One behavioural concern — whether the registry an engine validates is the
 * document it was given: a cleared path declared twice is malformed input, and a
 * lossy parse that keeps only the last record must not make it valid.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("clearance-integrity", "clearance integrity parity");

/**
 * Integration: the merge-mode half of the behavioral-parity corpus.
 *
 * One behavioural concern — what a merge-mode binding produces: the top-level
 * key merge, the `mcp` merge by server name and the retargeted QMD index.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("merge-mode", "merge mode parity");

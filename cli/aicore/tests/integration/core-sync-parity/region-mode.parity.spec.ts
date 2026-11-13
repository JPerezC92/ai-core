/**
 * Integration: the region-mode half of the behavioral-parity corpus.
 *
 * One behavioural concern — what a region-mode binding produces: the spliced
 * core region, the preserved project region, the refreshed frontmatter, the
 * pending entry and the reconciliation report. Exercised against a real
 * engine over a real temporary filesystem (T4), with per-test isolation (T18).
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("region-mode", "region mode parity");

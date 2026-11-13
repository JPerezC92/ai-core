/**
 * Integration: the destination-root half of the behavioral-parity corpus.
 *
 * One behavioural concern — how the destination instruction root is chosen: a
 * `role: root` source maps to the detected root rather than to its own path, and
 * `--root` names that path when the destination holds no detectable root.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("root-role", "destination root parity");

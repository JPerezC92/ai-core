/**
 * Integration: the `--bind` / `--bind-raw` declaration half of the
 * behavioral-parity corpus.
 *
 * One behavioural concern — what a CLI binding declaration does: append a
 * mapping before preflight, be refused when malformed, fail closed when it
 * contradicts the persisted destinations, and carry the raw form's consequences.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("binding-declarations", "binding declaration parity");

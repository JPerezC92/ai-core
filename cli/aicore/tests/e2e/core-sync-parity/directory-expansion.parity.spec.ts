/**
 * End to end: the directory-expansion half of the behavioral-parity corpus.
 *
 * One behavioural concern — which entries a cleared directory root puts in a
 * distribution set: dependency installation directories and `.git` stay out, a
 * non-regular entry is neither followed nor delivered, and the skill's own
 * scripts, references and tests still ship.
 */

import { describeConcern } from "#support/core-sync-parity/describe-concern.ts";

describeConcern("directory-expansion", "directory expansion parity");

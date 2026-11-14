/** Process adapter: fetch `opencode models` output and map it to models. */

import { spawnSync } from 'node:child_process';

import type { Model, ModelSource } from '#scripts/op_model_lookup/domain/catalog.ts';
import { ModelSourceFailure, parseRecords } from '#scripts/op_model_lookup/domain/catalog.ts';

const NOT_FOUND = 'ERROR: `opencode` not found on PATH. Cannot list models.';
const TIMEOUT_MS = 60_000;

/** ModelSource adapter over the local `opencode models` process. */
export class OpencodeModelSource implements ModelSource {
  /**
   * Run the checked live command and return the valid parsed models.
   *
   * A missing executable, failed child execution, or timeout is raised as a
   * ModelSourceFailure; no fallback or partial output is ever returned.
   */
  fetch(): readonly Model[] {
    const result = spawnSync('opencode', ['models'], {
      encoding: 'utf8',
      timeout: TIMEOUT_MS,
      maxBuffer: 32 * 1024 * 1024,
    });

    const error = result.error as NodeJS.ErrnoException | undefined;
    if (error?.code === 'ENOENT') throw new ModelSourceFailure(NOT_FOUND);
    if (error?.code === 'ETIMEDOUT' || result.signal !== null) {
      throw new ModelSourceFailure('ERROR: `opencode models` timed out.');
    }
    if (error !== undefined) throw new ModelSourceFailure(`ERROR: \`opencode models\` failed:\n${error.message}`);
    if (result.status !== 0) {
      throw new ModelSourceFailure(
        `ERROR: \`opencode models\` failed (exit ${String(result.status)}):\n${result.stderr ?? ''}`,
      );
    }
    return parseRecords(result.stdout ?? '').models;
  }
}

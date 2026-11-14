/** models.ts — fetch and filter the opencode models available to this user.
 *
 * Usage:
 *   node .agents/skills/op-model/scripts/models.ts            list all available models grouped by provider
 *   node .agents/skills/op-model/scripts/models.ts "<query>"  list matching records only (JSON lines)
 *
 * Output record fields: config, id, provider, name, cost_in, cost_out.
 * Matching normalizes both sides: lowercase, strips non-alphanumerics, and
 * matches against the config name AND the human name.
 */

import { execute } from '#scripts/op_model_lookup/application/find_models.ts';
import { ModelSourceFailure } from '#scripts/op_model_lookup/domain/catalog.ts';
import { runCli } from '#scripts/op_model_lookup/infrastructure/cli.ts';
import { OpencodeModelSource } from '#scripts/op_model_lookup/infrastructure/process.ts';

/** Compose the live model source with the use case and CLI renderer. */
export function main(argv: readonly string[]): number {
  const query = argv[0] ?? '';
  try {
    const outcome = execute(query, new OpencodeModelSource());
    return runCli(outcome, query);
  } catch (error) {
    if (error instanceof ModelSourceFailure) {
      process.stderr.write(`${error.message}\n`);
      return 1;
    }
    throw error;
  }
}

process.exitCode = main(process.argv.slice(2));

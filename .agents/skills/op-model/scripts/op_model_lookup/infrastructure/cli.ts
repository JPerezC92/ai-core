/** CLI adapter: render model selections and map outcomes to process exit codes. */

import type { LookupOutcome, Model } from '#scripts/op_model_lookup/domain/catalog.ts';

/**
 * Render a number the way the reference implementation does: a float field
 * always keeps a decimal point, so a zero cost prints as `0.0` and not `0`.
 */
function pythonFloat(value: number): string {
  return Number.isInteger(value) ? `${value}.0` : String(value);
}

/** Serialize one model as a JSON object with the six contract fields in order. */
function renderRecord(model: Model): string {
  const entries: Array<readonly [string, string]> = [
    ['config', JSON.stringify(model.config)],
    ['id', JSON.stringify(model.id)],
    ['provider', JSON.stringify(model.provider)],
    ['name', JSON.stringify(model.name)],
    ['cost_in', pythonFloat(model.costIn)],
    ['cost_out', pythonFloat(model.costOut)],
  ];
  return `{${entries.map(([key, value]) => `${JSON.stringify(key)}: ${value}`).join(', ')}}`;
}

/** Render the models grouped by provider, noting name and cost only when known. */
function renderGrouped(selection: readonly Model[]): string {
  const byProvider = new Map<string, Model[]>();
  for (const model of selection) {
    const bucket = byProvider.get(model.provider);
    if (bucket === undefined) byProvider.set(model.provider, [model]);
    else bucket.push(model);
  }

  const lines: string[] = [];
  for (const provider of [...byProvider.keys()].sort()) {
    lines.push(`## ${provider}`);
    const models = [...byProvider.get(provider)!].sort((left, right) =>
      left.config < right.config ? -1 : left.config > right.config ? 1 : 0);
    for (const model of models) {
      let line = `  ${model.config}`;
      if (model.name !== model.id) line += ` | ${model.name}`;
      if (model.costIn !== 0 || model.costOut !== 0) {
        line += ` | in:${pythonFloat(model.costIn)} per 1M | out:${pythonFloat(model.costOut)} per 1M`;
      }
      lines.push(line);
    }
    lines.push('');
  }
  return `${lines.join('\n')}\n`;
}

/** Render the selected models as JSON lines (query) or a grouped listing. */
export function renderSelection(selection: readonly Model[], query: string): string {
  if (selection.length === 0) return '';
  if (query !== '') return selection.map(model => `${renderRecord(model)}\n`).join('');
  return renderGrouped(selection);
}

function isOutcome(value: LookupOutcome): value is Exclude<LookupOutcome, readonly Model[]> {
  return !Array.isArray(value);
}

/** Render the lookup outcome and return the process exit code. */
export function runCli(outcome: LookupOutcome, query: string): number {
  if (isOutcome(outcome)) {
    process.stderr.write(`${outcome.message}\n`);
    return 1;
  }
  process.stdout.write(renderSelection(outcome, query));
  return 0;
}

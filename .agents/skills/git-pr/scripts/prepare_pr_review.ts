/** Compose PR review content preparation commands from local files. */

import { basename } from 'node:path';

import { execute as validate } from '#scripts/pr_content/application/validate_final_body.ts';
import { extractBody } from '#scripts/pr_content/domain/body_validation.ts';
import type { ReviewPreparationError } from '#scripts/pr_content/domain/records.ts';
import { createText, readText } from '#scripts/pr_content/infrastructure/filesystem.ts';

interface Command {
  readonly kind: 'initialize' | 'validate';
  readonly draft: string | null;
  readonly baseline: string | null;
  readonly current: string | null;
  readonly workingBody: string;
  readonly decisions: string | null;
}

type ParseResult = { readonly ok: true; readonly command: Command } | { readonly ok: false; readonly message: string };

/** The reference serializes dataclass fields with Python's default JSON spacing. */
function pythonJsonObject(entries: ReadonlyArray<readonly [string, string]>): string {
  const body = entries.map(([key, value]) => `${JSON.stringify(key)}: ${JSON.stringify(value)}`).join(', ');
  return `{${body}}`;
}

function usage(program: string): string {
  return `usage: ${program} [-h] {initialize,validate} ...`;
}

function parseCli(args: readonly string[]): ParseResult {
  if (args.length === 0) return { ok: false, message: 'the following arguments are required: command' };
  const [command, ...rest] = args;
  if (command !== 'initialize' && command !== 'validate') {
    return { ok: false, message: `argument command: invalid choice: '${command}' (choose from 'initialize', 'validate')` };
  }

  const values = new Map<string, string>();
  for (let index = 0; index < rest.length; index++) {
    const arg = rest[index]!;
    if (!arg.startsWith('--')) return { ok: false, message: `unrecognized arguments: ${arg}` };
    const value = rest[index + 1];
    if (value === undefined) return { ok: false, message: `argument ${arg}: expected one argument` };
    values.set(arg.slice(2), value);
    index += 1;
  }

  const required = command === 'initialize' ? ['draft', 'working-body'] : ['baseline', 'current', 'working-body'];
  for (const field of required) {
    if (!values.has(field)) return { ok: false, message: `the following arguments are required: --${field}` };
  }
  for (const field of values.keys()) {
    if (![...required, 'decisions'].includes(field)) {
      return { ok: false, message: `unrecognized arguments: --${field}` };
    }
  }

  return {
    ok: true,
    command: {
      kind: command,
      draft: values.get('draft') ?? null,
      baseline: values.get('baseline') ?? null,
      current: values.get('current') ?? null,
      workingBody: values.get('working-body')!,
      decisions: values.get('decisions') ?? null,
    },
  };
}

/** Decode supplied files, invoke the operation and serialize results at delivery. */
export function main(argv: readonly string[], program = 'prepare_pr_review.ts'): number {
  const parsed = parseCli(argv);
  if (!parsed.ok) {
    process.stderr.write(`${usage(program)}\n${basename(program)}: error: ${parsed.message}\n`);
    return 2;
  }

  try {
    const command = parsed.command;
    if (command.kind === 'initialize') {
      const body = extractBody(readText(command.draft!));
      if (typeof body !== 'string') {
        const failure = body as ReviewPreparationError;
        process.stdout.write(`${pythonJsonObject([['code', failure.code], ['message', failure.message]])}\n`);
        return 1;
      }
      createText(command.workingBody, body);
    } else {
      const baseline: unknown = JSON.parse(readText(command.baseline!));
      const current: unknown = JSON.parse(readText(command.current!));
      const candidate = readText(command.workingBody);
      const decisions: unknown = command.decisions === null ? null : JSON.parse(readText(command.decisions));
      const outcome = validate({ baseline, current, body: candidate, decisions });
      if ('code' in outcome) {
        process.stdout.write(`${pythonJsonObject([['code', outcome.code], ['message', outcome.message]])}\n`);
        return 1;
      }
    }
    process.stdout.write(`${pythonJsonObject([['status', 'prepared'], ['command', command.kind]])}\n`);
    return 0;
  } catch (error) {
    process.stderr.write(`input/output failure: ${(error as Error).message}\n`);
    return 2;
  }
}

process.exitCode = main(process.argv.slice(2), basename(process.argv[1] ?? 'prepare_pr_review.ts'));

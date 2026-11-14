/** Composition root: parse CLI, wire adapters, serialize diagnostics, and map exits. */

import { basename } from 'node:path';

import { CheckText } from '#scripts/markdown_text_pkg/application/check_text.ts';
import type { CheckOutcome, DomainError, Finding } from '#scripts/markdown_text_pkg/domain/models.ts';
import { EDITOR_DRIFT_ID } from '#scripts/markdown_text_pkg/domain/models.ts';
import { canonicalHex } from '#scripts/markdown_text_pkg/domain/policy.ts';
import { escapeForDiagnostic } from '#scripts/markdown_text_pkg/domain/scan.ts';
import { MarkdownFilesystem, PolicyLoader } from '#scripts/markdown_text_pkg/infrastructure/filesystem.ts';

export interface CliRequest {
  readonly policy: string;
  readonly editor: string | null;
  readonly paths: readonly string[];
}

export type CliParse = { readonly ok: true; readonly request: CliRequest } | { readonly ok: false; readonly message: string };

/** Parse `--policy PATH [--check-editor PATH] PATH [PATH ...]` with the reference wording. */
export function parseCli(args: readonly string[]): CliParse {
  let policy: string | undefined;
  let editor: string | null = null;
  const paths: string[] = [];
  const unknown: string[] = [];

  for (let index = 0; index < args.length; index++) {
    const arg = args[index]!;
    if (arg === '--policy' || arg === '--check-editor') {
      const value = args[index + 1];
      if (value === undefined) {
        return { ok: false, message: `argument ${arg}: expected one argument` };
      }
      if (arg === '--policy') policy = value;
      else editor = value;
      index += 1;
      continue;
    }
    if (arg.startsWith('--policy=')) {
      policy = arg.slice('--policy='.length);
      continue;
    }
    if (arg.startsWith('--check-editor=')) {
      editor = arg.slice('--check-editor='.length);
      continue;
    }
    if (arg.startsWith('-')) {
      unknown.push(arg);
      continue;
    }
    paths.push(arg);
  }

  if (unknown.length > 0) return { ok: false, message: `unrecognized arguments: ${unknown.join(' ')}` };
  if (policy === undefined) return { ok: false, message: 'the following arguments are required: --policy' };
  if (paths.length === 0) return { ok: false, message: 'the following arguments are required: paths' };
  return { ok: true, request: { policy, editor, paths } };
}

export function usage(program: string): string {
  return `usage: ${program} --policy PATH [--check-editor PATH] PATH [PATH ...]`;
}

function formatFailure(failure: DomainError): string {
  return escapeForDiagnostic(`${failure.code}: ${failure.message}`);
}

function sanitizeAsciiKey(key: string): string {
  const parts: string[] = [];
  for (const char of key) {
    const codepoint = char.codePointAt(0) ?? 0;
    if (codepoint >= 0x20 && codepoint <= 0x7e) parts.push(char);
    else parts.push(canonicalHex(codepoint));
  }
  return parts.join('');
}

/**
 * Serialize one stdout diagnostic. The character position and code point are
 * preserved; the descriptive Unicode character name is intentionally omitted.
 */
export function formatFinding(finding: Finding): string {
  const path = escapeForDiagnostic(finding.path.replaceAll('\\', '/'));
  if (finding.kind === 'utf8') {
    return `${path}:${finding.line}:${finding.column}: ${escapeForDiagnostic(finding.severity)} `
      + `${escapeForDiagnostic(finding.ruleId)} byte ${finding.byteOffset}`;
  }
  if (finding.kind === 'editor-drift') {
    const join = (keys: readonly string[]) => keys.map(sanitizeAsciiKey).join(',');
    return `${path}: error ${EDITOR_DRIFT_ID} `
      + `missing=${join(finding.missing)} extra=${join(finding.extra)} mismatched=${join(finding.mismatched)}`;
  }
  return `${path}:${finding.line}:${finding.column}: ${escapeForDiagnostic(finding.severity)} `
    + `${escapeForDiagnostic(finding.ruleId)} ${canonicalHex(finding.codepoint)} ${escapeForDiagnostic(finding.excerpt)}`;
}

function isErrorFinding(finding: Finding): boolean {
  if (finding.kind === 'editor-drift') return true;
  return finding.severity === 'error';
}

/** Write findings to stdout, failures to stderr, and map the CLI exit code. */
export function render(outcome: CheckOutcome): number {
  for (const failed of outcome.failures) process.stderr.write(`${formatFailure(failed)}\n`);
  for (const finding of outcome.findings) process.stdout.write(`${formatFinding(finding)}\n`);
  if (outcome.failures.length > 0) return 2;
  if (outcome.findings.some(isErrorFinding)) return 1;
  return 0;
}

export function main(argv: readonly string[], program = 'check_markdown_text.ts'): number {
  const parsed = parseCli(argv);
  if (!parsed.ok) {
    process.stderr.write(`${usage(program)}\n${basename(program)}: error: ${parsed.message}\n`);
    return 2;
  }
  const outcome = new CheckText(new PolicyLoader(), new MarkdownFilesystem())
    .execute(parsed.request.policy, parsed.request.paths, parsed.request.editor);
  return render(outcome);
}

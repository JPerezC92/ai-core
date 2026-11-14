/** Filesystem adapters: policy load, Markdown discovery, and JSON object reads. */

import { lstatSync, readFileSync, readdirSync } from 'node:fs';
import { extname, normalize, resolve, sep } from 'node:path';

import type {
  DiscoverResult, DomainError, FileTarget, Policy,
} from '#scripts/markdown_text_pkg/domain/models.ts';
import { CODE_INPUT, CODE_IO, CODE_POLICY, isDomainError } from '#scripts/markdown_text_pkg/domain/models.ts';
import type { FilePort, PolicyPort } from '#scripts/markdown_text_pkg/domain/ports.ts';
import { parsePolicy } from '#scripts/markdown_text_pkg/domain/policy.ts';

const EXCLUDED_DIRECTORY_NAMES = new Set([
  '.git', '.secrets', 'secrets', 'output', '.venv', 'venv', 'node_modules', '__pycache__',
]);

const decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });

type RootKind =
  | { readonly kind: 'file'; readonly absNorm: string }
  | { readonly kind: 'directory'; readonly absNorm: string }
  | { readonly kind: 'failure'; readonly failure: DomainError };

/** Normalize separators for display and sort without following the target. */
export function posixDisplay(path: string): string {
  return path.replaceAll('\\', '/');
}

/** Absolute normalized path identity without resolving or following links. */
export function absNorm(path: string): string {
  return normalize(resolve(path));
}

function failure(code: string, message: string): DomainError {
  return { code, message };
}

function isMarkdownName(name: string): boolean {
  return extname(name).toLowerCase() === '.md';
}

function inspectRegularFile(
  raw: string, display: string, code: string, label: string,
): string | DomainError {
  const target = absNorm(raw);
  let info;
  try {
    info = lstatSync(target);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      return failure(code, `missing ${label} path: ${display}`);
    }
    return failure(CODE_IO, `unreadable ${label} path: ${display}`);
  }
  if (info.isSymbolicLink()) return failure(code, `symlink not followed: ${display}`);
  if (!info.isFile()) return failure(code, `${label} path is not a regular file: ${display}`);
  return target;
}

function readBytes(target: string, display: string, code: string): Uint8Array | DomainError {
  try {
    return new Uint8Array(readFileSync(target));
  } catch {
    return failure(code, `unreadable path: ${display}`);
  }
}

function decodeText(raw: Uint8Array): string | undefined {
  try {
    return decoder.decode(raw);
  } catch {
    return undefined;
  }
}

/** The first object key that repeats at the same nesting level, if any. */
export function firstDuplicateJsonKey(text: string): string | undefined {
  type Frame = { object: boolean; keys: Set<string>; expectKey: boolean };
  const stack: Frame[] = [];
  let index = 0;
  while (index < text.length) {
    const char = text[index]!;
    if (char === '"') {
      const start = index;
      index += 1;
      while (index < text.length) {
        const current = text[index]!;
        if (current === '\\') {
          index += 2;
          continue;
        }
        if (current === '"') break;
        index += 1;
      }
      const raw = text.slice(start, index + 1);
      index += 1;
      const frame = stack[stack.length - 1];
      if (frame !== undefined && frame.object && frame.expectKey) {
        const key = JSON.parse(raw) as string;
        if (frame.keys.has(key)) return key;
        frame.keys.add(key);
        frame.expectKey = false;
      }
      continue;
    }
    if (char === '{') {
      stack.push({ object: true, keys: new Set(), expectKey: true });
      index += 1;
    } else if (char === '[') {
      stack.push({ object: false, keys: new Set(), expectKey: false });
      index += 1;
    } else if (char === '}' || char === ']') {
      stack.pop();
      index += 1;
    } else {
      if (char === ',') {
        const frame = stack[stack.length - 1];
        if (frame !== undefined && frame.object) frame.expectKey = true;
      }
      index += 1;
    }
  }
  return undefined;
}

function decodeJsonObject(
  text: string, code: string, label: string,
): Record<string, unknown> | DomainError {
  const duplicate = firstDuplicateJsonKey(text);
  if (duplicate !== undefined) {
    return failure(code, `invalid ${label} JSON: duplicate key ${duplicate}`);
  }
  let decoded: unknown;
  try {
    decoded = JSON.parse(text);
  } catch (error) {
    return failure(code, `invalid ${label} JSON: ${(error as Error).message}`);
  }
  if (typeof decoded !== 'object' || decoded === null || Array.isArray(decoded)) {
    return failure(code, `${label} JSON root must be an object`);
  }
  return decoded as Record<string, unknown>;
}

export class PolicyLoader implements PolicyPort {
  /** Read, decode, and validate a caller-supplied policy document. */
  load(path: string): Policy | DomainError {
    const display = posixDisplay(path);
    const inspected = inspectRegularFile(path, display, CODE_POLICY, 'policy');
    if (typeof inspected !== 'string') return inspected;
    const raw = readBytes(inspected, display, CODE_POLICY);
    if (isDomainError(raw)) return raw;
    const text = decodeText(raw);
    if (text === undefined) return failure(CODE_POLICY, `policy is not valid UTF-8: ${display}`);
    const decoded = decodeJsonObject(text, CODE_POLICY, 'policy');
    if (isDomainError(decoded)) return decoded;
    return parsePolicy(decoded);
  }
}

export class MarkdownFilesystem implements FilePort {
  /** Inspect explicit roots, enter real directories, and skip excluded descendants. */
  discover(roots: readonly string[]): DiscoverResult {
    const targets: FileTarget[] = [];
    const failures: DomainError[] = [];
    const seenRoots = new Set<string>();
    const seenFiles = new Set<string>();

    const ordered = [...roots].sort((left, right) => {
      const a = posixDisplay(left);
      const b = posixDisplay(right);
      return a < b ? -1 : a > b ? 1 : 0;
    });

    for (const raw of ordered) {
      const display = posixDisplay(raw);
      const target = absNorm(raw);
      if (seenRoots.has(target)) continue;
      seenRoots.add(target);

      const root = this.#classifyRoot(raw, display, target);
      if (root.kind === 'failure') {
        failures.push(root.failure);
        continue;
      }
      if (root.kind === 'directory') {
        this.#walkDirectory(root.absNorm, display, seenFiles, targets, failures);
        continue;
      }
      if (seenFiles.has(root.absNorm)) continue;
      seenFiles.add(root.absNorm);
      targets.push({ displayPath: display, absNorm: root.absNorm });
    }
    return { targets, failures };
  }

  readBytes(target: FileTarget): Uint8Array | DomainError {
    return readBytes(target.absNorm, target.displayPath, CODE_IO);
  }

  /** Load editor settings JSON without following symlinks. */
  loadJsonObject(path: string): Record<string, unknown> | DomainError {
    const display = posixDisplay(path);
    const inspected = inspectRegularFile(path, display, CODE_INPUT, 'editor');
    if (typeof inspected !== 'string') return inspected;
    const raw = readBytes(inspected, display, CODE_IO);
    if (isDomainError(raw)) return raw;
    const text = decodeText(raw);
    if (text === undefined) return failure(CODE_INPUT, `editor is not valid UTF-8: ${display}`);
    return decodeJsonObject(text, CODE_INPUT, 'editor');
  }

  #classifyRoot(raw: string, display: string, target: string): RootKind {
    let info;
    try {
      info = lstatSync(target);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return { kind: 'failure', failure: failure(CODE_INPUT, `missing path: ${display}`) };
      }
      return { kind: 'failure', failure: failure(CODE_IO, `unreadable path: ${display}`) };
    }
    if (info.isSymbolicLink()) {
      return { kind: 'failure', failure: failure(CODE_INPUT, `symlink not followed: ${display}`) };
    }
    if (info.isFile()) {
      if (!isMarkdownName(raw)) {
        return { kind: 'failure', failure: failure(CODE_INPUT, `not a markdown file: ${display}`) };
      }
      return { kind: 'file', absNorm: target };
    }
    if (info.isDirectory()) return { kind: 'directory', absNorm: target };
    return { kind: 'failure', failure: failure(CODE_INPUT, `not a markdown file or directory: ${display}`) };
  }

  #walkDirectory(
    directory: string, display: string, seenFiles: Set<string>,
    targets: FileTarget[], failures: DomainError[],
  ): void {
    let entries;
    try {
      entries = readdirSync(directory, { withFileTypes: true });
    } catch {
      failures.push(failure(CODE_IO, `unreadable path: ${display}`));
      return;
    }
    entries.sort((left, right) => left.name < right.name ? -1 : left.name > right.name ? 1 : 0);
    for (const entry of entries) {
      const childDisplay = `${display.replace(/\/+$/, '')}/${entry.name}`;
      if (entry.isSymbolicLink()) continue;
      if (entry.isDirectory()) {
        if (EXCLUDED_DIRECTORY_NAMES.has(entry.name.toLowerCase())) continue;
        this.#walkDirectory(`${directory}${sep}${entry.name}`, childDisplay, seenFiles, targets, failures);
        continue;
      }
      if (!entry.isFile()) continue;
      if (!isMarkdownName(entry.name)) continue;
      const child = absNorm(`${directory}${sep}${entry.name}`);
      if (seenFiles.has(child)) continue;
      seenFiles.add(child);
      targets.push({ displayPath: childDisplay, absNorm: child });
    }
  }
}

/** Pure Markdown byte scan against a validated policy; no filesystem IO. */

import type { Finding, Policy, ScalarFinding, Utf8Finding } from './models.ts';
import { classifyCodepoint } from './policy.ts';

const NON_PRINTABLE = /[\p{gc=Cc}\p{gc=Cf}\p{gc=Cs}\p{gc=Co}\p{gc=Cn}\p{gc=Zl}\p{gc=Zp}\p{gc=Zs}]/u;

/** Replace control and other non-printable code points with U+XXXX spellings. */
export function escapeForDiagnostic(text: string): string {
  const parts: string[] = [];
  for (const char of text) parts.push(isSafeDiagnosticChar(char) ? char : toSpelling(char));
  return parts.join('');
}

function isSafeDiagnosticChar(char: string): boolean {
  if (char === ' ') return true;
  return !NON_PRINTABLE.test(char);
}

function toSpelling(char: string): string {
  return `U+${(char.codePointAt(0) ?? 0).toString(16).toUpperCase().padStart(4, '0')}`;
}

/** The index of the first ill-formed byte in a UTF-8 sequence, if any. */
export function firstInvalidUtf8Index(bytes: Uint8Array): number | undefined {
  let index = 0;
  while (index < bytes.length) {
    const lead = bytes[index]!;
    if (lead <= 0x7f) {
      index += 1;
      continue;
    }
    let needed: number;
    let codepoint: number;
    let minimum: number;
    if (lead >= 0xc2 && lead <= 0xdf) {
      needed = 1; codepoint = lead & 0x1f; minimum = 0x80;
    } else if (lead >= 0xe0 && lead <= 0xef) {
      needed = 2; codepoint = lead & 0x0f; minimum = 0x800;
    } else if (lead >= 0xf0 && lead <= 0xf4) {
      needed = 3; codepoint = lead & 0x07; minimum = 0x10000;
    } else {
      return index;
    }
    for (let offset = 1; offset <= needed; offset++) {
      const next = bytes[index + offset];
      if (next === undefined || (next & 0xc0) !== 0x80) return index;
      codepoint = (codepoint << 6) | (next & 0x3f);
    }
    if (codepoint < minimum || codepoint > 0x10ffff || (codepoint >= 0xd800 && codepoint <= 0xdfff)) {
      return index;
    }
    index += needed + 1;
  }
  return undefined;
}

function decodeValid(bytes: Uint8Array): string {
  return new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes);
}

/** Scan decoded scalars against policy rules; stop after the first invalid UTF-8. */
export function scanMarkdownBytes(data: Uint8Array, policy: Policy, path: string): readonly Finding[] {
  const display = path.replaceAll('\\', '/');
  const invalid = firstInvalidUtf8Index(data);
  if (invalid !== undefined) return [utf8Finding(data, policy, display, invalid)];

  const text = decodeValid(data);
  const findings: ScalarFinding[] = [];
  const lines = text.split('\n');
  for (const [lineIndex, line] of lines.entries()) {
    const excerpt = escapeForDiagnostic(line);
    let column = 0;
    for (const char of line) {
      column += 1;
      const codepoint = char.codePointAt(0) ?? 0;
      const rule = classifyCodepoint(policy, codepoint);
      if (rule === undefined) continue;
      findings.push({
        kind: 'scalar',
        path: display,
        line: lineIndex + 1,
        column,
        severity: rule.severity,
        ruleId: rule.id,
        codepoint,
        excerpt,
      });
    }
  }
  return findings;
}

function utf8Finding(data: Uint8Array, policy: Policy, path: string, start: number): Utf8Finding {
  const prefix = data.subarray(0, start);
  let line = 1;
  for (const byte of prefix) if (byte === 0x0a) line += 1;
  let lastNewline = -1;
  for (const [index, byte] of prefix.entries()) if (byte === 0x0a) lastNewline = index;
  const tail = decodeValid(prefix.subarray(lastNewline + 1));
  const envelope = policy.decoding.invalidSequence;
  return {
    kind: 'utf8',
    path,
    line,
    column: 1 + [...tail].length,
    severity: envelope.severity,
    ruleId: envelope.id,
    byteOffset: start + 1,
  };
}

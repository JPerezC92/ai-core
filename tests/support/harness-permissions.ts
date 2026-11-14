/**
 * Effective harness permission resolution, read for the repository contract tests.
 *
 * The semantics modelled here are the product's documented ones: whole-value
 * wildcard matching of the raw command string, rules combined in order with the
 * last match winning, and a shell resource that is the command text itself.
 * Only rules whose action is `shell` or `*` participate; the default effect is
 * `ask`.
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { REPO_ROOT } from "#support/agent-spec-documents.ts";

export type PermissionRule = {
  readonly action?: string;
  readonly resource?: string;
  readonly effect?: string;
};

export type HarnessConfig = {
  readonly permissions?: readonly PermissionRule[];
  readonly agents?: Readonly<
    Record<string, { readonly permissions?: readonly PermissionRule[] }>
  >;
};

/** The base policy every agent starts with; only its shell-relevant row is exercised. */
export const BASE_PERMISSION_POLICY: readonly PermissionRule[] = [
  { action: "*", resource: "*", effect: "allow" },
];

export const HARNESS_CONFIG_PATH = join(REPO_ROOT, "opencode.jsonc");

/**
 * Removes `//` comments from JSONC text outside double-quoted strings.
 *
 * A `//` inside a string is part of the value — a URL, for example — and is
 * kept, so only a comment that starts outside a string is dropped.
 */
export function stripJsoncComments(text: string): string {
  let output = "";
  let inString = false;
  let escaped = false;
  let index = 0;

  while (index < text.length) {
    const character = text[index]!;
    if (inString) {
      output += character;
      if (escaped) {
        escaped = false;
      } else if (character === "\\") {
        escaped = true;
      } else if (character === '"') {
        inString = false;
      }
      index += 1;
      continue;
    }
    if (character === '"') {
      inString = true;
      output += character;
      index += 1;
      continue;
    }
    if (character === "/" && text[index + 1] === "/") {
      while (index < text.length && text[index] !== "\n") index += 1;
      continue;
    }
    output += character;
    index += 1;
  }

  return output;
}

/** Reads and parses the tracked harness configuration. */
export function readHarnessConfig(path: string = HARNESS_CONFIG_PATH): HarnessConfig {
  return JSON.parse(stripJsoncComments(readFileSync(path, "utf8"))) as HarnessConfig;
}

function globPattern(pattern: string): RegExp {
  let escaped = "";
  for (const character of pattern) {
    if (character === "*") {
      escaped += ".*";
    } else if (character === "?") {
      escaped += ".";
    } else {
      escaped += character.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&");
    }
  }
  return new RegExp(`^(?:${escaped})$`, "u");
}

/**
 * Whether a shell resource pattern matches a command string.
 *
 * A shell resource is matched as a whole value against the raw command text,
 * with `*` and `?` as wildcards, and a pattern ending in ` *` also matches the
 * command without its arguments.
 */
export function resourceMatches(pattern: string, command: string): boolean {
  if (globPattern(pattern).test(command)) return true;
  if (pattern.endsWith(" *")) return globPattern(pattern.slice(0, -2)).test(command);
  return false;
}

/**
 * The effective effect of a shell command for an agent.
 *
 * Rules combine in order — the base policy, then the global rules, then the
 * agent's own rules — and the last matching rule wins.
 */
export function effectivePermission(
  config: HarnessConfig,
  agent: string,
  command: string,
): string {
  const rules: PermissionRule[] = [
    ...BASE_PERMISSION_POLICY,
    ...(config.permissions ?? []),
    ...(config.agents?.[agent]?.permissions ?? []),
  ];

  let effect = "ask";
  for (const rule of rules) {
    if (rule.action !== "shell" && rule.action !== "*") continue;
    if (resourceMatches(rule.resource ?? "", command)) effect = rule.effect ?? "ask";
  }
  return effect;
}

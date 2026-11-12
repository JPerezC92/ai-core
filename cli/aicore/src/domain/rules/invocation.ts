/**
 * Domain rules: command-line parsing.
 *
 * Pure per scripts-shape P1: typed data in, typed data out, no IO.
 */

import {
  ADVANCED_COMMANDS,
  PLANNED_EDITORS,
  REVISION_ENV_VAR,
  REVISION_PATTERN,
  SUPPORTED_EDITORS,
  type AdvancedCommand,
  type SupportedEditor,
} from "#domain/constants.ts";
import { fail, succeed, type Result } from "#domain/failures.ts";
import { isSupportedEditor } from "./selection.ts";

export type ParsedInvocation =
  | {
      readonly kind: "sync";
      readonly target?: string;
      readonly editor?: string;
      readonly revision?: string;
      readonly help: boolean;
    }
  | {
      readonly kind: "advanced";
      readonly command: AdvancedCommand;
      readonly passthrough: readonly string[];
      readonly help: boolean;
    }
  | { readonly kind: "help" };

const SYNC_FLAGS = ["--target", "--editor", "--source-revision"] as const;

type SyncFlag = (typeof SYNC_FLAGS)[number];

function isAdvancedCommand(value: string): value is AdvancedCommand {
  return (ADVANCED_COMMANDS as readonly string[]).includes(value);
}

/**
 * Parse the argument vector into a typed invocation.
 *
 * The wrapper owns only the flags it documents. Any other argument is either a
 * recognized advanced-command passthrough or a usage failure, so an unknown flag
 * can never be silently dropped before the engine sees it.
 */
export function parseInvocation(argv: readonly string[]): Result<ParsedInvocation> {
  const [command, ...rest] = argv;
  if (command === undefined || command === "--help" || command === "-h") {
    return succeed({ kind: "help" });
  }

  if (isAdvancedCommand(command)) {
    return succeed({
      kind: "advanced",
      command,
      passthrough: rest,
      help: rest.includes("--help") || rest.includes("-h"),
    });
  }

  if (command !== "sync") {
    return fail(
      "unavailable-configuration",
      `unknown command "${command}". Use "sync", or one of: ${ADVANCED_COMMANDS.join(", ")}.`,
    );
  }

  const collected: Partial<Record<SyncFlag, string>> = {};
  let help = false;

  for (let index = 0; index < rest.length; index += 1) {
    const argument = rest[index];
    if (argument === undefined) {
      continue;
    }
    if (argument === "--help" || argument === "-h") {
      help = true;
      continue;
    }
    if (!(SYNC_FLAGS as readonly string[]).includes(argument)) {
      return fail(
        "unavailable-configuration",
        `unrecognized option "${argument}" for "sync". Supported options: ${SYNC_FLAGS.join(", ")}.`,
      );
    }

    const flag = argument as SyncFlag;
    const value = rest[index + 1];
    if (value === undefined || value.startsWith("--")) {
      return fail("unavailable-configuration", `option "${flag}" requires a value.`);
    }
    if (collected[flag] !== undefined) {
      return fail(
        "unavailable-configuration",
        `option "${flag}" was supplied more than once.`,
      );
    }
    collected[flag] = value;
    index += 1;
  }

  return succeed({
    kind: "sync",
    ...(collected["--target"] === undefined ? {} : { target: collected["--target"] }),
    ...(collected["--editor"] === undefined ? {} : { editor: collected["--editor"] }),
    ...(collected["--source-revision"] === undefined
      ? {}
      : { revision: collected["--source-revision"] }),
    help,
  });
}

/**
 * Resolve the requested editor.
 *
 * A named editor the engine does not implement is refused by name; the CLI never
 * substitutes OpenCode for a requested Cursor run.
 */
export function resolveEditor(requested: string): Result<SupportedEditor> {
  if (isSupportedEditor(requested)) {
    return succeed(requested);
  }
  if ((PLANNED_EDITORS as readonly string[]).includes(requested)) {
    return fail(
      "unsupported-editor",
      `editor "${requested}" is not implemented: this build distributes only ` +
        `${SUPPORTED_EDITORS.join(", ")}. Nothing was written. Cursor agent support ` +
        "is tracked separately and is not available yet.",
    );
  }
  return fail(
    "unsupported-editor",
    `unknown editor "${requested}". Supported: ${SUPPORTED_EDITORS.join(", ")}.`,
  );
}

/**
 * Resolve the source revision from an explicit value, then the operator setting.
 *
 * The CLI never runs Git, so an absent or malformed revision is a reported
 * failure rather than an implicit lookup. Syntax is checked with the engine's own
 * rule so the engine is never reached with a value it would have to reject.
 */
export function resolveRevision(
  flag: string | undefined,
  setting: string | undefined,
): Result<string> {
  const candidate = flag ?? setting;
  if (candidate === undefined || candidate.trim() === "") {
    return fail(
      "invalid-revision",
      "no source revision available. Supply --source-revision <40-hex> or set " +
        `$${REVISION_ENV_VAR}. This tool never runs Git: the revision must come from ` +
        "the release owner, so Herald 📯 (Release Manager) remains the only Git executor.",
    );
  }
  if (!REVISION_PATTERN.test(candidate)) {
    return fail(
      "invalid-revision",
      `source revision "${candidate}" is not a 40-character lowercase hex string.`,
    );
  }
  return succeed(candidate);
}

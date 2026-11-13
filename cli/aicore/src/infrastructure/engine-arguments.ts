/**
 * Infrastructure: the engine's command-line syntax, mapped to its request.
 *
 * The engine's public command line is part of its published contract:
 * `--source`, `--destination`, `--bindings` and `--source-revision` for every
 * command, `--editor` for every command, plus `--bind`, `--bind-raw`,
 * `--bind-cleared` and `--root` for `init`. This module turns that vector into
 * the engine's request record in a single mapping step (contract C4), so the
 * engine receives the command the wrapper always forwarded and the operator's
 * syntax keeps working unchanged.
 *
 * A vector the engine's own syntax rejects produces the result the engine
 * produced for it before: exit `2`, the diagnostic on standard error, and
 * nothing on standard output. The diagnostic keeps the engine's own program
 * name, because the operator asked the engine for that command.
 *
 * The revision's own syntax rule stays with the engine, which reports it in the
 * same words the engine's command line always used.
 */

import type { CommandName } from "#domain/synchronization/constants.ts";

import type { CoreSyncEngineRequest } from "./core-sync-engine.ts";

/** The commands the engine exposes, in the engine's own order. */
const COMMANDS: readonly CommandName[] = ["check", "apply", "init"];

/** The options that carry a value. */
const VALUE_FLAGS: readonly string[] = [
  "--source",
  "--destination",
  "--bindings",
  "--source-revision",
  "--bind",
  "--bind-raw",
  "--root",
  "--editor",
];

/** The options that stand alone. */
const BOOLEAN_FLAGS: readonly string[] = ["--bind-cleared"];

/** The outcome of mapping one command line onto the engine's request. */
export type EngineArgumentMapping =
  | { readonly ok: true; readonly request: CoreSyncEngineRequest }
  | { readonly ok: false; readonly message: string };

/** How one option name resolves to the option it names. */
type FlagResolution =
  | { readonly kind: "resolved"; readonly flag: string }
  | { readonly kind: "ambiguous"; readonly candidates: readonly string[] }
  | { readonly kind: "unknown" };

/**
 * Map one engine command line onto the engine's request.
 *
 * The mapping is faithful to the engine's own argument syntax: an option's
 * value may follow it or be attached with `=`, an unambiguous prefix names an
 * option, and a repeated option keeps the last value while a repeatable option
 * keeps every value.
 */
export function toEngineRequest(
  command: string,
  arguments_: readonly string[],
): EngineArgumentMapping {
  if (!isCommand(command)) {
    return {
      ok: false,
      message:
        `core-sync: error: invalid choice: '${command}' ` +
        `(choose from ${COMMANDS.map((name) => `'${name}'`).join(", ")})`,
    };
  }

  const values = new Map<string, string>();
  const bind: string[] = [];
  const bindRaw: string[] = [];
  const flags = new Set<string>();
  const unrecognized: string[] = [];

  for (let index = 0; index < arguments_.length; index += 1) {
    const argument = arguments_[index];
    if (argument === undefined) {
      continue;
    }
    if (!argument.startsWith("--")) {
      unrecognized.push(argument);
      continue;
    }

    const separator = argument.indexOf("=");
    const name = separator === -1 ? argument : argument.slice(0, separator);
    const attached = separator === -1 ? undefined : argument.slice(separator + 1);

    const resolution = resolveFlag(name);
    if (resolution.kind === "unknown") {
      unrecognized.push(argument);
      continue;
    }
    if (resolution.kind === "ambiguous") {
      return {
        ok: false,
        message:
          `core-sync ${command}: error: ambiguous option: ${name} ` +
          `could match ${resolution.candidates.join(", ")}`,
      };
    }

    const flag = resolution.flag;
    if (BOOLEAN_FLAGS.includes(flag)) {
      if (attached !== undefined) {
        return {
          ok: false,
          message:
            `core-sync ${command}: error: argument ${flag}: ` +
            `ignored explicit argument '${attached}'`,
        };
      }
      flags.add(flag);
      continue;
    }

    let value = attached;
    if (value === undefined) {
      const next = arguments_[index + 1];
      if (next === undefined || next.startsWith("-")) {
        return {
          ok: false,
          message: `core-sync ${command}: error: argument ${flag}: expected one argument`,
        };
      }
      value = next;
      index += 1;
    }

    if (flag === "--bind") {
      bind.push(value);
    } else if (flag === "--bind-raw") {
      bindRaw.push(value);
    } else {
      values.set(flag, value);
    }
  }

  const sourceRoot = values.get("--source");
  const destinationRoot = values.get("--destination");
  const bindingsPath = values.get("--bindings");
  const sourceRevision = values.get("--source-revision");

  if (
    sourceRoot === undefined ||
    destinationRoot === undefined ||
    bindingsPath === undefined ||
    sourceRevision === undefined
  ) {
    const missing: string[] = [];
    if (sourceRoot === undefined) {
      missing.push("--source");
    }
    if (destinationRoot === undefined) {
      missing.push("--destination");
    }
    if (bindingsPath === undefined) {
      missing.push("--bindings");
    }
    if (sourceRevision === undefined) {
      missing.push("--source-revision");
    }
    return {
      ok: false,
      message:
        `core-sync ${command}: error: the following arguments are required: ` +
        missing.join(", "),
    };
  }
  if (unrecognized.length > 0) {
    return {
      ok: false,
      message:
        `core-sync ${command}: error: unrecognized arguments: ` +
        unrecognized.join(" "),
    };
  }

  return {
    ok: true,
    request: {
      command,
      sourceRoot,
      destinationRoot,
      bindingsPath,
      sourceRevision,
      bind,
      bindRaw,
      bindCleared: flags.has("--bind-cleared"),
      root: values.get("--root"),
      editor: values.get("--editor"),
    },
  };
}

/** Whether the named command is one the engine exposes. */
function isCommand(command: string): command is CommandName {
  return (COMMANDS as readonly string[]).includes(command);
}

/**
 * Resolve one option name to the option it names.
 *
 * An exact name wins over a prefix, and a prefix that names more than one
 * option is ambiguous — the rule the engine's own argument syntax follows.
 */
function resolveFlag(name: string): FlagResolution {
  const known = [...VALUE_FLAGS, ...BOOLEAN_FLAGS];
  if (known.includes(name)) {
    return { kind: "resolved", flag: name };
  }
  const candidates = known.filter((flag) => flag.startsWith(name));
  if (candidates.length === 1) {
    return { kind: "resolved", flag: candidates[0] as string };
  }
  if (candidates.length > 1) {
    return { kind: "ambiguous", candidates };
  }
  return { kind: "unknown" };
}

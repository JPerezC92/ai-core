/**
 * Domain constants and closed value sets for the AICore synchronization CLI.
 *
 * Data-only per scripts-shape P1: this module holds no functions and performs
 * no IO. Process exit statuses are deliberately absent — they are transport and
 * belong to the delivery edge.
 */

/** Editors whose agent distribution the engine actually implements today. */
export const SUPPORTED_EDITORS = ["opencode"] as const;

/** Editors the CLI can name in an error without implying support. */
export const PLANNED_EDITORS = ["cursor"] as const;

export type SupportedEditor = (typeof SUPPORTED_EDITORS)[number];

/** Canonical bindings file, relative to the destination project root. */
export const BINDINGS_RELATIVE_PATH = ".aicore/core.yaml";

/** Operator-local configuration, relative to the AICore checkout root. */
export const LOCAL_CONFIG_RELATIVE_PATH = ".aicore/local.json";

/** Overrides where the operator-local selection file lives. */
export const LOCAL_CONFIG_OVERRIDE_ENV_VAR = "AICORE_LOCAL_CONFIG";

/** Revision supplied through the environment, never obtained by running Git. */
export const REVISION_ENV_VAR = "AICORE_SOURCE_REVISION";

/** Accepted source-revision syntax, unchanged from the engine's own rule. */
export const REVISION_PATTERN = /^[0-9a-f]{40}$/;

/** Commands the engine exposes and the wrapper forwards unchanged. */
export const ADVANCED_COMMANDS = ["check", "apply", "init"] as const;

export type AdvancedCommand = (typeof ADVANCED_COMMANDS)[number];

/**
 * Domain constants and closed value sets for the AICore synchronization CLI.
 *
 * Data-only per scripts-shape P1: this module holds no functions and performs
 * no IO. Process exit statuses are deliberately absent — they are transport and
 * belong to the delivery edge.
 */

import {
  EDITOR_PROFILES,
  type EditorProfile,
} from "#domain/synchronization/editor-profile.ts";

/**
 * Editors whose agent distribution the engine implements.
 *
 * The set is the synchronization engine's own, so the wrapper never accepts an
 * editor the engine cannot deliver.
 */
export const SUPPORTED_EDITORS = EDITOR_PROFILES;

export type SupportedEditor = EditorProfile;

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

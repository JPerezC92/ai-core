/**
 * OpenCode-only local secret directory and ignore-rule writes.
 *
 * After payload writes, an OpenCode destination needs the directory the shipped
 * configuration's `{file:../.secrets/context7-api-key}` reference names. The
 * directory is created when missing; an existing credential file is never read
 * or rewritten; a missing credential file is created empty. The destination
 * Git ignore file gains an effective `.secrets/` rule first. Cursor enrollment
 * performs none of this.
 *
 * The setup is planned before it runs: the operation learns which writes it
 * will perform, from the facts the pending payload writes leave behind, and
 * the write-target preflight validates those writes before the first one
 * happens. The executor itself stays the one that performs them.
 */

import type { EditorProfile } from "#domain/synchronization/editor-profile.ts";
import type {
	DestinationFiles,
	FilesystemLayout,
	PlannedMutation,
	PlannedPayload,
} from "#domain/synchronization/ports.ts";
import { withSecretsIgnore } from "#domain/synchronization/secrets-ignore.ts";
import { projectedPayloadText } from "#domain/synchronization/write-targets.ts";

const CONFIGURATION_RELATIVE = ".opencode/opencode.jsonc";
const GITIGNORE_RELATIVE = ".gitignore";
const SECRETS_DIRECTORY = ".secrets";
const SECRET_FILE_RELATIVE = ".secrets/context7-api-key";

/** Collaborators the OpenCode secret writes need. */
export type OpenCodeSecretsDependencies = {
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
};

/** The paths the OpenCode secret setup touches inside one destination. */
export type OpenCodeSecretsPaths = {
	readonly configuration: string;
	readonly gitignore: string;
	readonly secretsDirectory: string;
	readonly secretFile: string;
};

/** What the secret setup reads, and what it will change. */
export type OpenCodeSecretsPreparation = {
	readonly destinationRoot: string;
	readonly paths: OpenCodeSecretsPaths;
	/** Whether the OpenCode configuration is present after the pending writes. */
	readonly configurationPresent: boolean;
	/** Whether the ignore file's contents are read to plan the secret writes. */
	readonly readsIgnore: boolean;
};

/** Facts observed safely or projected from pending synchronization writes. */
type OpenCodeSecretsFacts = {
	readonly configurationPresent: boolean;
	readonly gitignore: string | null;
	readonly secretsDirectoryExists: boolean;
	readonly secretFileExists: boolean;
};

type OpenCodeSecretsMutation =
	| { readonly kind: "directory"; readonly path: string }
	| { readonly kind: "file"; readonly path: string; readonly bytes: Uint8Array };

/** The paths the OpenCode secret setup touches. */
function openCodeSecretsPaths(destinationRoot: string, layout: FilesystemLayout): OpenCodeSecretsPaths {
	return {
		configuration: layout.join(destinationRoot, CONFIGURATION_RELATIVE),
		gitignore: layout.join(destinationRoot, GITIGNORE_RELATIVE),
		secretsDirectory: layout.join(destinationRoot, SECRETS_DIRECTORY),
		secretFile: layout.join(destinationRoot, SECRET_FILE_RELATIVE),
	};
}

/**
 * Observe what the secret setup will read, before it reads it.
 *
 * The configuration is present when the pending writes leave it there, and the
 * ignore file is read only when the setup has to plan its rule and no pending
 * write already decides the file's content.
 */
export async function prepareOpenCodeSecrets(
	editor: EditorProfile,
	destinationRoot: string,
	payload: readonly PlannedPayload[],
	layout: FilesystemLayout,
): Promise<OpenCodeSecretsPreparation> {
	const paths = openCodeSecretsPaths(destinationRoot, layout);
	const configurationPresent = await presentAfterWrites(paths.configuration, payload, layout);
	const readsIgnore =
		editor === "opencode" && configurationPresent && projectedPayloadText(paths.gitignore, payload) === undefined;
	return { destinationRoot, paths, configurationPresent, readsIgnore };
}

/** Plan only the writes that secret setup will perform after synchronization. */
function planOpenCodeSecrets(editor: EditorProfile, facts: OpenCodeSecretsFacts): readonly OpenCodeSecretsMutation[] {
	if (editor !== "opencode" || !facts.configurationPresent) {
		return [];
	}
	const mutations: OpenCodeSecretsMutation[] = [];
	const nextIgnore = withSecretsIgnore(facts.gitignore);
	if (nextIgnore !== facts.gitignore) {
		mutations.push({
			kind: "file",
			path: GITIGNORE_RELATIVE,
			bytes: new TextEncoder().encode(nextIgnore),
		});
	}
	if (!facts.secretsDirectoryExists) {
		mutations.push({ kind: "directory", path: SECRETS_DIRECTORY });
	}
	if (!facts.secretFileExists) {
		mutations.push({ kind: "file", path: SECRET_FILE_RELATIVE, bytes: new Uint8Array() });
	}
	return mutations;
}

/**
 * The secret mutations the setup performs, as the mutations the preflight
 * validates.
 *
 * The ignore file's content is the content the pending writes leave behind,
 * or the content disk holds — read only after the read preflight cleared it.
 * An existing credential is never read: only its absence is observed.
 */
export async function planOpenCodeSecretWrites(
	editor: EditorProfile,
	preparation: OpenCodeSecretsPreparation,
	payload: readonly PlannedPayload[],
	dependencies: OpenCodeSecretsDependencies,
): Promise<readonly PlannedMutation[]> {
	const { destinations, layout } = dependencies;
	const { destinationRoot, paths, configurationPresent } = preparation;
	// A destination that gets no secret setup has no ignore file to read: the
	// read happens only where the read preflight cleared that path.
	if (editor !== "opencode" || !configurationPresent) {
		return [];
	}
	const projected = projectedPayloadText(paths.gitignore, payload);
	const gitignore = projected !== undefined ? projected : await destinations.readText(paths.gitignore);
	const facts: OpenCodeSecretsFacts = {
		configurationPresent,
		gitignore,
		// The executor creates the directory only when the path is absent, so the
		// planner observes existence alone: a path that exists as a file is
		// neither created nor refused here.
		secretsDirectoryExists: await layout.exists(paths.secretsDirectory),
		secretFileExists: await layout.exists(paths.secretFile),
	};
	return planOpenCodeSecrets(editor, facts).map((mutation) => ({
		path: layout.join(destinationRoot, mutation.path),
		kind: mutation.kind === "directory" ? "directory-create" : "file-write",
		owner: mutation.kind === "directory" ? "directory" : "secret",
	}));
}

/**
 * Create missing OpenCode secret paths and the ignore rule, without overwriting
 * an existing secret file.
 */
export async function ensureOpenCodeSecrets(
	editor: EditorProfile,
	destinationRoot: string,
	dependencies: OpenCodeSecretsDependencies,
): Promise<void> {
	if (editor !== "opencode") {
		return;
	}
	const { destinations, layout } = dependencies;
	const paths = openCodeSecretsPaths(destinationRoot, layout);
	if (!(await layout.exists(paths.configuration))) {
		return;
	}
	const existingIgnore = await destinations.readText(paths.gitignore);
	const nextIgnore = withSecretsIgnore(existingIgnore);
	if (nextIgnore !== existingIgnore) {
		await destinations.writeBytes(paths.gitignore, new TextEncoder().encode(nextIgnore));
	}

	if (!(await layout.exists(paths.secretsDirectory))) {
		await layout.ensureDirectory(paths.secretsDirectory);
	}

	if (!(await layout.exists(paths.secretFile))) {
		await destinations.writeBytes(paths.secretFile, new Uint8Array());
	}
}

/** Return whether a path is present once the pending writes have been applied. */
async function presentAfterWrites(
	path: string,
	payload: readonly PlannedPayload[],
	layout: FilesystemLayout,
): Promise<boolean> {
	const projected = projectedPayloadText(path, payload);
	if (projected !== undefined) {
		return projected !== null;
	}
	return layout.exists(path);
}

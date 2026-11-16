/**
 * OpenCode-only local secret directory and ignore-rule writes.
 *
 * After payload writes, an OpenCode destination needs the directory the shipped
 * configuration's `{file:../.secrets/context7-api-key}` reference names. The
 * directory is created when missing; an existing credential file is never read
 * or rewritten; a missing credential file is created empty. The destination
 * Git ignore file gains an effective `.secrets/` rule first. Cursor enrollment
 * performs none of this.
 */

import type { EditorProfile } from "#domain/synchronization/editor-profile.ts";
import type { DestinationFiles, FilesystemLayout } from "#domain/synchronization/ports.ts";
import { withSecretsIgnore } from "#domain/synchronization/secrets-ignore.ts";

const GITIGNORE_RELATIVE = ".gitignore";
const SECRETS_DIRECTORY = ".secrets";
const SECRET_FILE_RELATIVE = ".secrets/context7-api-key";

/** Collaborators the OpenCode secret writes need. */
export type OpenCodeSecretsDependencies = {
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
};

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
	const configurationPath = layout.join(destinationRoot, ".opencode/opencode.jsonc");
	if (!(await layout.exists(configurationPath))) {
		return;
	}
	const gitignorePath = layout.join(destinationRoot, GITIGNORE_RELATIVE);
	const existingIgnore = await destinations.readText(gitignorePath);
	const nextIgnore = withSecretsIgnore(existingIgnore);
	if (nextIgnore !== existingIgnore) {
		await destinations.writeBytes(gitignorePath, new TextEncoder().encode(nextIgnore));
	}

	const secretsDirectory = layout.join(destinationRoot, SECRETS_DIRECTORY);
	if (!(await layout.exists(secretsDirectory))) {
		await layout.ensureDirectory(secretsDirectory);
	}

	const secretFile = layout.join(destinationRoot, SECRET_FILE_RELATIVE);
	if (!(await layout.exists(secretFile))) {
		await destinations.writeBytes(secretFile, new Uint8Array());
	}
}

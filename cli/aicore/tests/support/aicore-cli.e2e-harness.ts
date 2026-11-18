/**
 * Shared harness for the end-to-end suite.
 *
 * Contract T15: shared test data lives in a helper, never inline. This module
 * also isolates operator state (T18): every invocation points the CLI at a
 * throwaway selection file, so the developer's real selection is never read or
 * written, and an interrupted or concurrent run cannot corrupt it.
 */

import { execFile } from "node:child_process";
import { copyFile, mkdir, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

import { createTemporaryRoot, disposeTemporaryRoot } from "./disposable-root.ts";

const run = promisify(execFile);

/** Prefix that identifies a root this harness owns. */
const FIXTURE_PREFIX = "aicore-e2e-";

export const CHECKOUT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "..");
export const CLI_ENTRY = join(CHECKOUT, "cli", "aicore", "src", "main.ts");

/** A valid 40-character lowercase hex revision. */
export const REVISION = "0123456789abcdef0123456789abcdef01234567";

/** A disposable destination directory plus its isolated selection file. */
export type Fixture = {
	readonly destination: string;
	readonly configPath: string;
	readonly root: string;
	dispose(): Promise<void>;
};

export async function createFixture(
	options: { readonly agentsBody?: string; readonly editor?: string } = {},
): Promise<Fixture> {
	const { root, prefix } = await createTemporaryRoot(FIXTURE_PREFIX);
	const destination = join(root, "destination");
	await mkdir(destination, { recursive: true });
	await writeFile(
		join(destination, "AGENTS.md"),
		options.agentsBody ?? "# Fixture project\n\nA disposable destination for end-to-end verification.\n",
		"utf8",
	);
	if (options.editor !== undefined) {
		await mkdir(join(destination, ".aicore"), { recursive: true });
		await writeFile(join(destination, ".aicore", "core.yaml"), enrolledBindings(options.editor), "utf8");
	}

	return {
		destination,
		configPath: join(root, "local.json"),
		root,
		async dispose(): Promise<void> {
			// Ownership is re-validated here, immediately before deletion.
			await disposeTemporaryRoot(root, prefix);
		},
	};
}

/**
 * Files copied into the representative source. The clearance registry lists
 * only these paths (directory-root keys for the skill and agent trees).
 */
export const REPRESENTATIVE_FILES = [
	"AGENTS.md",
	".opencode/opencode.jsonc",
	".opencode/agents/forge.md",
	".opencode/agents/lumen.md",
	".agents/skills/op-model/SKILL.md",
	".agents/skills/git-commit/SKILL.md",
	".agents/skills/incident-workflow/references/local-symptoms-template.md",
	".agents/skills/incident-workflow/references/local-problems-template.md",
	".aicore/core/odd/tasks/_template.md",
	".aicore/core/odd/features/_template.md",
	".aicore/core/knowledge/agents.md",
	".aicore/core/knowledge/diagnostics/symptoms.md",
	".aicore/core/knowledge/diagnostics/problems.md",
	".aicore/core/knowledge/diagnostics/diagnostic-guidance.md",
] as const;

/** Agent documents the representative source actually ships. */
export const REPRESENTATIVE_AGENT_FILES = ["forge.md", "lumen.md"] as const;

const REPRESENTATIVE_CLEARED: Readonly<Record<string, Readonly<Record<string, unknown>>>> = {
	"AGENTS.md": { mode: "region", role: "root" },
	".opencode/opencode.jsonc": {
		mode: "merge",
		omit_mcp_servers: ["system-one"],
		editors: {
			opencode: { destination: ".opencode/opencode.jsonc" },
			cursor: { omitted: true },
		},
	},
	".aicore/core/knowledge/agents.md": { mode: "region" },
	".aicore/core/knowledge/diagnostics/": { mode: "region" },
	".aicore/core/odd/tasks/_template.md": { mode: "raw" },
	".aicore/core/odd/features/_template.md": { mode: "raw" },
	".agents/skills/op-model/": { mode: "raw" },
	".agents/skills/git-commit/": { mode: "raw" },
	".agents/skills/incident-workflow/": { mode: "raw" },
	".opencode/agents/": {
		mode: "region",
		editors: {
			opencode: { destination: ".opencode/agents/" },
			cursor: { destination: ".cursor/agents/" },
		},
	},
};

/** A disposable destination whose source is the representative tree, not the checkout. */
export type RepresentativeFixture = Fixture & {
	readonly source: string;
};

/**
 * Copy real checkout bytes for a small set that still proves region, raw, merge,
 * root role, one agent pair, one optional skill directory, one kept skill, the
 * protected baselines, and the managed ODD template. Isolation is the same
 * mkdtemp root the fixture already owns.
 */
export async function createRepresentativeSource(root: string): Promise<string> {
	const source = join(root, "source");
	await mkdir(source, { recursive: true });
	for (const relative of REPRESENTATIVE_FILES) {
		const target = join(source, relative);
		await mkdir(dirname(target), { recursive: true });
		await copyFile(join(CHECKOUT, relative), target);
	}
	await writeFile(
		join(source, "distribution-clearance.json"),
		`${JSON.stringify({ schema: 1, cleared: REPRESENTATIVE_CLEARED }, null, 2)}\n`,
		"utf8",
	);
	return source;
}

export async function createRepresentativeFixture(
	options: { readonly agentsBody?: string; readonly editor?: string } = {},
): Promise<RepresentativeFixture> {
	const fixture = await createFixture(options);
	const source = await createRepresentativeSource(fixture.root);
	return { ...fixture, source };
}

export type Invocation = {
	readonly status: number;
	readonly stdout: string;
	readonly stderr: string;
};

/**
 * Invoke the CLI as an operator would.
 *
 * `AICORE_LOCAL_CONFIG` redirects the selection file, so no test reads or writes
 * the real operator selection.
 */
export async function invoke(
	arguments_: readonly string[],
	options: {
		readonly fixture: Fixture;
		readonly revision?: string | undefined;
	},
): Promise<Invocation> {
	const env: Record<string, string> = {};
	for (const [key, value] of Object.entries(process.env)) {
		if (value !== undefined) {
			env[key] = value;
		}
	}
	delete env["AICORE_SOURCE_REVISION"];
	delete env["AICORE_LOCAL_CONFIG"];

	if (options.revision !== undefined && options.revision !== "") {
		env["AICORE_SOURCE_REVISION"] = options.revision;
	}
	env["AICORE_LOCAL_CONFIG"] = options.fixture.configPath;

	try {
		const { stdout, stderr } = await run(process.execPath, [CLI_ENTRY, ...arguments_], {
			cwd: CHECKOUT,
			env,
			maxBuffer: 32 * 1024 * 1024,
			windowsHide: true,
		});
		return { status: 0, stdout, stderr };
	} catch (error) {
		const failure = error as { code?: number | string; stdout?: string; stderr?: string };
		// A numeric code is a child process that exited with that status. Anything
		// else — a spawn failure, a missing executable — is not an exit status, and
		// reporting it as one would let a run that never happened look like exit 1.
		if (typeof failure.code !== "number") {
			throw error;
		}
		return {
			status: failure.code,
			stdout: failure.stdout ?? "",
			stderr: failure.stderr ?? "",
		};
	}
}

/**
 * Invoke with the default valid revision.
 */
export function invokeWithRevision(arguments_: readonly string[], fixture: Fixture): Promise<Invocation> {
	return invoke(arguments_, { fixture, revision: REVISION });
}

/**
 * The bindings of a destination already enrolled for one editor profile.
 *
 * The bindings file is the destination's own state: it records the editor the
 * destination was enrolled for, so a fixture can stand in for an enrollment
 * without running one.
 */
function enrolledBindings(editor: string): string {
	return ["schema: 1", `core_revision: ${REVISION}`, `editor: ${editor}`, "bindings: []", "pending: []", ""].join(
		"\n",
	);
}

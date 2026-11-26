/** Build offline review evidence inputs, an isolated Git fixture, and invalid variants. */

import { spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import type {
	Artifact,
	AttributionPolicy,
	ChangedFile,
	ScanResult,
	Snapshot,
} from "#scripts/attribution_scan/domain/records.ts";
import type { LocalInventory } from "#scripts/pr_review/domain/records.ts";
import { FIXTURE_HEAD_SHA, makeSyntheticPolicy } from "./attribution-fixtures.ts";

// The capture schema belongs to the content skill; this half builds opaque capture
// objects for the workflow comparison and never re-declares their fields.
export type Capture = Record<string, unknown>;

/** The PR number every published metadata and review fixture carries. */
const PUBLICATION_PR_NUMBER = 80;

/** The title the creation-stage publication document carries. */
const PUBLICATION_TITLE = "feat(review): prepare publication";

/** The named defects an invalid inventory fixture may carry. */
export type InventoryDefect = "missing" | "extra" | "duplicate";

/** The capture fields a divergence fixture may change. */
export type RemoteField = "number" | "headRefOid" | "body";

/** Create a canonical passing body; overrides target named textual fields. */
export function createBody(overrides: { item?: string; head?: string } = {}): string {
	const item = overrides.item ?? "Inspect the change and confirm the intended result";
	const head = overrides.head ?? FIXTURE_HEAD_SHA;
	return (
		"## Summary\n- Preserve this unrelated explanation exactly.\n\n" +
		`## Test plan\n- [x] ${item}\n` +
		"- [x] Inspect the regression and confirm it is absent\n\n" +
		"## Findings / blockers\nNo findings.\n\n" +
		"## Test evidence\n- PR: `#80`\n" +
		`- Immutable head SHA: \`${head}\`\n` +
		"- Base: `origin/main`\n" +
		`- Scope command: \`git diff "origin/main"...${FIXTURE_HEAD_SHA}\`\n\n` +
		"| Test-plan item | Literal action/input | Observed result | Executor |\n" +
		"|---|---|---|---|\n" +
		`| ${item} | Inspect the change | Expected result observed | Reviewer |\n` +
		"| Inspect the regression and confirm it is absent | Inspect regression | Absent | Reviewer |\n\n" +
		"[PASS] — Required checks are recorded and no findings remain.\n"
	);
}

/** Create owner-supplied metadata with explicit typed overrides. */
export function createMetadata(options: { number?: number; head?: string; body?: string } = {}): Capture {
	return {
		number: options.number ?? PUBLICATION_PR_NUMBER,
		headRefOid: options.head ?? FIXTURE_HEAD_SHA,
		baseRefName: "main",
		headRefName: "feat/release/body",
		state: "OPEN",
		title: "feat(release): prepare review",
		body: options.body ?? createBody(),
	};
}

/** Create a remote identity, head, or body change. */
export function createDivergence(field: RemoteField): Capture {
	if (field === "number") return createMetadata({ number: 81 });
	if (field === "headRefOid") return createMetadata({ head: "b".repeat(40) });
	return createMetadata({ body: "Changed remotely" });
}

/** Create owner-supplied metadata carrying a key outside the documented seven. */
export function createMetadataWithUndeclaredKey(field = "url"): Capture {
	return {
		...createMetadata(),
		[field]: "https://example.invalid/JPerezC92/ai-core/pull/80",
	};
}

/** Create scanner-compatible complete content including a deleted path. */
export function createSnapshot(): Snapshot {
	return {
		schema: 1,
		pr_number: 80,
		head_sha: FIXTURE_HEAD_SHA,
		base: "origin/main",
		artifacts: [
			{ surface: "pr-title", source: "PR #80 title", content: "feat(release): prepare review" },
			{ surface: "pr-body", source: "PR #80 body", content: createBody() },
			{ surface: "commit-message", source: FIXTURE_HEAD_SHA, content: "feat(release): prepare review" },
		],
		changed_files: [
			{ path: "src/current.py", content: "value = 1\n" },
			{ path: "src/deleted.py", content: "" },
		],
	};
}

/** Return the reconciled exact diff paths, including a deleted file. */
export function createPaths(): string[] {
	return ["src/current.py", "src/deleted.py"];
}

/** Return a path inventory carrying a value that is not a path string. */
export function createNonStringPathList(): unknown[] {
	return ["src/current.py", 2];
}

/** Create a local inventory whose commit artifact is not a commit message. */
export function createLocalInventoryWithForeignCommitSurface(): Record<string, unknown> {
	return {
		...createLocalInventory(),
		commit_messages: [{ surface: "pr-title", source: "wrong", content: "" }],
	};
}

/**
 * Create a valid local inventory whose values differ from the shared snapshot fixture.
 *
 * A distinct inventory isolates the acceptance of the exact documented field set
 * from the shared fixture, so the assertion cannot pass by fixture coincidence.
 */
export function createAlternateLocalInventory(): LocalInventory {
	return {
		schema: 1,
		pr_number: 81,
		head_sha: "b".repeat(40),
		base: "origin/release",
		commit_messages: [
			{ surface: "commit-message", source: "b".repeat(40), content: "feat(release): alternate local inventory" },
		],
		changed_files: [{ path: "src/alternate.py", content: "alternate = 1\n" }],
	};
}

/** Return the exact path inventory that matches the alternate local inventory. */
export function createAlternateLocalPaths(): string[] {
	return ["src/alternate.py"];
}

/** Create synthetic scanner policy data rather than duplicating approved tokens. */
export function createPolicy(): AttributionPolicy {
	return makeSyntheticPolicy();
}

/** Create a well-typed snapshot with a deliberately invalid inventory. */
export function createInvalidInventory(defect: InventoryDefect): Snapshot {
	const snapshot = createSnapshot();
	const files: ChangedFile[] = [...snapshot.changed_files];
	if (defect === "missing") {
		files.pop();
	} else if (defect === "extra") {
		files.push({ path: "src/unreviewed.py", content: "unreviewed" });
	} else {
		const first = files[0];
		if (first === undefined) throw new Error("the inventory fixture carries no changed file");
		files.push({ ...first });
	}
	return { ...snapshot, changed_files: files };
}

/** Create a deliberately incomplete snapshot missing commit artifacts. */
export function createSnapshotWithoutCommits(): Snapshot {
	const snapshot = createSnapshot();
	return { ...snapshot, artifacts: snapshot.artifacts.slice(0, 2) };
}

/** Create the expected existing-scanner output for the complete fixture. */
export function createCleanScanResult(): ScanResult {
	return {
		pr_number: 80,
		head_sha: FIXTURE_HEAD_SHA,
		base: "origin/main",
		matches: [],
		exclusions: [],
	};
}

/** Reuse immutable content fixtures without requiring scanner artifact assembly. */
export function createLocalInventory(): LocalInventory {
	const snapshot = createSnapshot();
	return {
		schema: 1,
		pr_number: snapshot.pr_number,
		head_sha: snapshot.head_sha,
		base: snapshot.base,
		commit_messages: snapshot.artifacts.slice(2),
		changed_files: snapshot.changed_files,
	};
}

/** Return authored local title distinct from the inventory commit subject. */
export function createLocalTitle(): string {
	return "feat(release): prepare local review";
}

/** Create the prepared receipt a generated body is handed over with. */
export function createPreparedReceipt(title: string): { readonly status: "prepared"; readonly title: string } {
	return { status: "prepared", title };
}

/** Return the title the creation-stage publication document carries. */
export function createPublicationTitle(): string {
	return PUBLICATION_TITLE;
}

/**
 * Create the creation-stage publication document the content skill generates a body from.
 *
 * The document belongs to the content skill's schema; this workflow builds it as an opaque
 * input and never re-declares that schema.
 */
export function createCreationPublicationDocument(): Capture {
	return {
		schemaVersion: 1,
		title: PUBLICATION_TITLE,
		summary: ["Adds the review preparation commands."],
		testPlan: [
			{ text: "Run the focused suite", status: "PENDING" },
			{ text: "Confirm the import map resolves", status: "PENDING" },
		],
	};
}

/**
 * Create the review-stage publication document that completes a creation-stage document.
 *
 * Every scheduled item records its observed result, so the document carries the review records
 * of one immutable head.
 */
export function createReviewPublicationDocument(creation: Capture = createCreationPublicationDocument()): Capture {
	const testPlan = creation["testPlan"];
	if (!Array.isArray(testPlan)) throw new Error("the creation document carries no test plan");
	return {
		...creation,
		testPlan: testPlan.map((item) => ({
			...(item as Capture),
			status: "PASSED",
			evidence: { action: "run", result: "passed", executor: "author" },
		})),
		review: {
			prNumber: PUBLICATION_PR_NUMBER,
			headSha: FIXTURE_HEAD_SHA,
			baseRef: "main",
			findings: [],
			debt: [],
			verdict: { kind: "PASS", basis: "Zero open findings; every required check is verified." },
		},
	};
}

/** Create a prepared receipt carrying a field the workflow must refuse. */
export function createReceiptWithUndeclaredField(): string {
	return JSON.stringify({ ...createPreparedReceipt("t"), bodySha256: "f".repeat(64) });
}

/** Create a path inventory that differs from the exact diff inventory. */
export function createUnexactPathInventory(): string[] {
	return ["src/unlisted-path"];
}

/** Return text that cannot be decoded as a publication document. */
export function createUndecodablePublicationText(): string {
	return "not json";
}

/**
 * Build the generated artifact handoff this workflow consumes.
 *
 * The receipt carries exactly a prepared status and the generated title; it holds no byte
 * identity of the input, the body or any earlier publication.
 */
export function createPublicationHandoff(): { receipt: string; body: string } {
	return { receipt: JSON.stringify(createPreparedReceipt(createLocalTitle())), body: createBody() };
}

/** Build expected scanner input from local authored title and working body. */
export function createLocalSnapshot(): Snapshot {
	const snapshot = createSnapshot();
	const artifacts: Artifact[] = snapshot.artifacts.map((artifact, index) =>
		index === 0 ? { ...artifact, content: createLocalTitle() } : artifact,
	);
	return { ...snapshot, artifacts };
}

export const GIT_SOURCE_PATH = "src/current.py";
export const GIT_BINARY_PATH = "src/binary.bin";
export const GIT_CHANGED_BINARY_PATH = "assets/evidence.png";
export const GIT_MALFORMED_TEXT_PATH = "src/latin1.txt";
export const GIT_REMOVED_PATH = "src/deleted.py";
export const GIT_METACHARACTER_PATH = "src/evil;touch injected.txt";
export const GIT_SIDE_EFFECT_NAME = "injected.txt";
export const GIT_RENAMED_FROM_PATH = "src/renamed-from.py";
export const GIT_RENAMED_TO_PATH = "src/renamed-to.py";
export const GIT_RENAMED_CONTENT = "renamed = 1\n";
export const GIT_BASE_ONLY_PATH = "src/base-only.py";
export const GIT_BASE_CONTENT = "value = 1\n";
export const GIT_CHANGED_CONTENT = "value = 2\n";
export const GIT_REMOVED_CONTENT = "gone = 1\n";
export const GIT_METACHARACTER_CONTENT = "value = 3\n";
export const GIT_BASE_ONLY_CONTENT = "side = 1\n";
export const GIT_BASE_ONLY_CHANGED_CONTENT = "side = 2\n";
export const GIT_BASE_MESSAGE = "feat: add source files";
export const GIT_CHANGED_MESSAGE = "feat: change source files";
export const GIT_BASE_ONLY_MESSAGE = "feat: change the base-only path";
export const GIT_ORPHAN_MESSAGE = "feat: an unrelated history";
export const GIT_SIDE_BRANCH = "feature/base-side";
export const GIT_HEAD_BRANCH = "feature/head-side";
export const GIT_BINARY_CONTENT = Buffer.from([0xff, 0xfe, 0x00, 0x6e, 0x6f, 0x74, 0x20, 0x74, 0x65, 0x78, 0x74, 0x0a]);
export const GIT_CHANGED_BINARY_CONTENT = Buffer.from([
	0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
]);
// No NUL byte, so Git still classifies this invalid UTF-8 body as text.
export const GIT_MALFORMED_TEXT_CONTENT = Buffer.from([0x66, 0x6f, 0x6f, 0x20, 0x80, 0x0a]);
export const GIT_REDIRECTING_VARIABLES = ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"];

/** One isolated two-commit repository and the values its readers must return. */
export type GitRepositoryFixture = {
	readonly directory: string;
	readonly base: string;
	readonly head: string;
	readonly orphanHead: string;
	readonly message: string;
	readonly changedPaths: string[];
	readonly deletedPaths: string[];
	readonly binaryPaths: string[];
	readonly bodies: Record<string, string>;
};

/** One isolated two-commit repository whose head changes only named paths. */
export type GitRangeFixture = {
	readonly directory: string;
	readonly base: string;
	readonly head: string;
	readonly changedPaths: string[];
	readonly binaryPaths: string[];
};

/** One repository whose base line holds a commit unreachable from its head. */
export type GitDivergentFixture = {
	readonly directory: string;
	readonly ancestor: string;
	readonly base: string;
	readonly head: string;
	readonly headPath: string;
	readonly headContent: string;
	readonly baseOnlyPath: string;
	readonly baseOnlyContent: string;
};

/** Return an environment without machine Git configuration or repository redirection. */
export function createFixtureEnvironment(): NodeJS.ProcessEnv {
	const environment: NodeJS.ProcessEnv = { ...process.env };
	environment["GIT_CONFIG_GLOBAL"] = process.platform === "win32" ? "nul" : "/dev/null";
	environment["GIT_CONFIG_NOSYSTEM"] = "1";
	environment["GIT_OPTIONAL_LOCKS"] = "0";
	for (const variable of GIT_REDIRECTING_VARIABLES) delete environment[variable];
	return environment;
}

/**
 * Stop Git's upward repository search at the supplied temporary root.
 *
 * Without this ceiling a temporary directory that happens to sit inside a
 * repository would resolve that repository, and the case could no longer prove
 * that a directory outside any repository is reported as a boundary failure.
 */
export function limitRepositorySearch(root: string): void {
	const separator = process.platform === "win32" ? ";" : ":";
	const previous = process.env["GIT_CEILING_DIRECTORIES"];
	const paths = previous === undefined ? [] : previous.split(separator);
	paths.push(root.replace(/\\/gu, "/"));
	process.env["GIT_CEILING_DIRECTORIES"] = paths.join(separator);
}

/** Run one fixture-only Git command inside the isolated temporary repository. */
export function runFixtureGit(directory: string, ...arguments_: string[]): string {
	const completed = spawnSync("git", arguments_, {
		cwd: directory,
		encoding: "utf8",
		shell: false,
		env: createFixtureEnvironment(),
	});
	if (completed.status !== 0) {
		throw new Error(`fixture git ${arguments_.join(" ")} failed: ${completed.stderr}`);
	}
	return completed.stdout;
}

/** Commit the staged fixture tree with local identity and return the new commit id. */
export function commitFixtureTree(directory: string, message: string): string {
	runFixtureGit(
		directory,
		"-c",
		"user.name=Fixture",
		"-c",
		"user.email=fixture@example.invalid",
		"-c",
		"commit.gpgsign=false",
		"commit",
		"--quiet",
		"--message",
		message,
	);
	return runFixtureGit(directory, "rev-parse", "HEAD").trim();
}

/** Create one commit object on the empty tree with no parent, so its history shares no ancestor. */
function createParentlessCommit(directory: string, message: string): string {
	// `mktree` reads its empty stdin as the empty listing, so the fixture needs no worktree
	// change and no branch checkout: only a dangling commit object is added.
	const emptyTree = runFixtureGit(directory, "mktree").trim();
	return runFixtureGit(
		directory,
		"-c",
		"user.name=Fixture",
		"-c",
		"user.email=fixture@example.invalid",
		"-c",
		"commit.gpgsign=false",
		"commit-tree",
		emptyTree,
		"-m",
		message,
	).trim();
}

/** Build two commits whose second change adds, renames, and deletes one path each. */
export function createCommittedRepository(directory: string): GitRepositoryFixture {
	mkdirSync(join(directory, "src"), { recursive: true });
	runFixtureGit(directory, "init", "--quiet");
	writeFileSync(join(directory, GIT_SOURCE_PATH), GIT_BASE_CONTENT, "utf8");
	writeFileSync(join(directory, GIT_REMOVED_PATH), GIT_REMOVED_CONTENT, "utf8");
	writeFileSync(join(directory, GIT_RENAMED_FROM_PATH), GIT_RENAMED_CONTENT, "utf8");
	// The binary body is committed in the base commit and never changed, so it
	// carries no changed path and the reader can read it without affecting the
	// diff inventory the other cases assert.
	writeFileSync(join(directory, GIT_BINARY_PATH), GIT_BINARY_CONTENT);
	runFixtureGit(directory, "add", "--all");
	const base = commitFixtureTree(directory, GIT_BASE_MESSAGE);
	mkdirSync(join(directory, "assets"), { recursive: true });
	writeFileSync(join(directory, GIT_CHANGED_BINARY_PATH), GIT_CHANGED_BINARY_CONTENT);
	writeFileSync(join(directory, GIT_SOURCE_PATH), GIT_CHANGED_CONTENT, "utf8");
	runFixtureGit(directory, "rm", "--quiet", GIT_REMOVED_PATH);
	writeFileSync(join(directory, GIT_METACHARACTER_PATH), GIT_METACHARACTER_CONTENT, "utf8");
	runFixtureGit(directory, "mv", GIT_RENAMED_FROM_PATH, GIT_RENAMED_TO_PATH);
	runFixtureGit(directory, "add", "--all");
	const head = commitFixtureTree(directory, GIT_CHANGED_MESSAGE);
	const orphanHead = createParentlessCommit(directory, GIT_ORPHAN_MESSAGE);
	return {
		directory,
		base,
		head,
		orphanHead,
		message: GIT_CHANGED_MESSAGE,
		changedPaths: [
			GIT_CHANGED_BINARY_PATH,
			GIT_SOURCE_PATH,
			GIT_REMOVED_PATH,
			GIT_METACHARACTER_PATH,
			GIT_RENAMED_TO_PATH,
		],
		deletedPaths: [GIT_REMOVED_PATH],
		binaryPaths: [GIT_CHANGED_BINARY_PATH],
		bodies: {
			[GIT_SOURCE_PATH]: GIT_CHANGED_CONTENT,
			[GIT_METACHARACTER_PATH]: GIT_METACHARACTER_CONTENT,
			[GIT_RENAMED_TO_PATH]: GIT_RENAMED_CONTENT,
		},
	};
}

/** Build two commits whose second change adds one binary path only. */
export function createBinaryOnlyRepository(directory: string): GitRangeFixture {
	mkdirSync(join(directory, "src"), { recursive: true });
	runFixtureGit(directory, "init", "--quiet");
	writeFileSync(join(directory, GIT_SOURCE_PATH), GIT_BASE_CONTENT, "utf8");
	runFixtureGit(directory, "add", "--all");
	const base = commitFixtureTree(directory, GIT_BASE_MESSAGE);
	mkdirSync(join(directory, "assets"), { recursive: true });
	writeFileSync(join(directory, GIT_CHANGED_BINARY_PATH), GIT_CHANGED_BINARY_CONTENT);
	runFixtureGit(directory, "add", "--all");
	const head = commitFixtureTree(directory, GIT_CHANGED_MESSAGE);
	return {
		directory,
		base,
		head,
		changedPaths: [GIT_CHANGED_BINARY_PATH],
		binaryPaths: [GIT_CHANGED_BINARY_PATH],
	};
}

/** Build two commits whose second change adds a binary path beside a non-UTF-8 text body. */
export function createMalformedTextRepository(directory: string): GitRangeFixture {
	mkdirSync(join(directory, "src"), { recursive: true });
	runFixtureGit(directory, "init", "--quiet");
	writeFileSync(join(directory, GIT_SOURCE_PATH), GIT_BASE_CONTENT, "utf8");
	runFixtureGit(directory, "add", "--all");
	const base = commitFixtureTree(directory, GIT_BASE_MESSAGE);
	mkdirSync(join(directory, "assets"), { recursive: true });
	writeFileSync(join(directory, GIT_CHANGED_BINARY_PATH), GIT_CHANGED_BINARY_CONTENT);
	writeFileSync(join(directory, GIT_MALFORMED_TEXT_PATH), GIT_MALFORMED_TEXT_CONTENT);
	runFixtureGit(directory, "add", "--all");
	const head = commitFixtureTree(directory, GIT_CHANGED_MESSAGE);
	return {
		directory,
		base,
		head,
		changedPaths: [GIT_CHANGED_BINARY_PATH, GIT_MALFORMED_TEXT_PATH],
		binaryPaths: [GIT_CHANGED_BINARY_PATH],
	};
}

/** Return one NUL-separated rename entry whose destination field is missing. */
export function createTruncatedStatusPayload(): string {
	return `R100\0${GIT_RENAMED_FROM_PATH}\0`;
}

/** Return one NUL-separated numstat entry whose deleted-line field is missing. */
export function createTruncatedNumstatPayload(): string {
	return `-\t${GIT_CHANGED_BINARY_PATH}\0`;
}

/** Build a head line and a base line that diverge after their shared ancestor. */
export function createDivergentRepository(directory: string): GitDivergentFixture {
	mkdirSync(join(directory, "src"), { recursive: true });
	runFixtureGit(directory, "init", "--quiet");
	writeFileSync(join(directory, GIT_SOURCE_PATH), GIT_BASE_CONTENT, "utf8");
	writeFileSync(join(directory, GIT_BASE_ONLY_PATH), GIT_BASE_ONLY_CONTENT, "utf8");
	runFixtureGit(directory, "add", "--all");
	const ancestor = commitFixtureTree(directory, GIT_BASE_MESSAGE);
	runFixtureGit(directory, "checkout", "--quiet", "-b", GIT_SIDE_BRANCH);
	writeFileSync(join(directory, GIT_BASE_ONLY_PATH), GIT_BASE_ONLY_CHANGED_CONTENT, "utf8");
	runFixtureGit(directory, "add", "--all");
	const base = commitFixtureTree(directory, GIT_BASE_ONLY_MESSAGE);
	runFixtureGit(directory, "checkout", "--quiet", "-b", GIT_HEAD_BRANCH, ancestor);
	writeFileSync(join(directory, GIT_SOURCE_PATH), GIT_CHANGED_CONTENT, "utf8");
	runFixtureGit(directory, "add", "--all");
	const head = commitFixtureTree(directory, GIT_CHANGED_MESSAGE);
	return {
		directory,
		ancestor,
		base,
		head,
		headPath: GIT_SOURCE_PATH,
		headContent: GIT_CHANGED_CONTENT,
		baseOnlyPath: GIT_BASE_ONLY_PATH,
		baseOnlyContent: GIT_BASE_ONLY_CHANGED_CONTENT,
	};
}

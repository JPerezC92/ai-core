/**
 * Data-only constants owned by the synchronization domain.
 *
 * The marker lines, the document schema versions, the clearance filename and
 * the shipped reconciliation-block text are the synchronization contract's own
 * vocabulary, so they live with the rules that use them (P1).
 */

/** The three binding modes a cleared source can resolve to. */
export type BindingMode = "region" | "raw" | "merge";

/** The three commands the engine performs. */
export type CommandName = "check" | "apply" | "init";

export const MODE_REGION: BindingMode = "region";
export const MODE_RAW: BindingMode = "raw";
export const MODE_MERGE: BindingMode = "merge";

/** Every accepted binding mode, in contract order. */
export const BINDING_MODES: readonly BindingMode[] = [MODE_REGION, MODE_RAW, MODE_MERGE];

/** The only clearance role: the destination's root runtime file. */
export const ROLE_ROOT = "root";

/** The clearance document's only accepted schema label. */
export const CLEARANCE_SCHEMA = 1;

/** The bindings and reconciliation-report schema version. */
export const SCHEMA_VERSION = 1;

export const CORE_BEGIN = "<!-- core:begin -->";
export const CORE_END = "<!-- core:end -->";
export const PROJECT_BEGIN = "<!-- project:begin -->";
export const PROJECT_END = "<!-- project:end -->";

export const RECONCILE_BEGIN = "<!-- core:reconcile:begin -->";
export const RECONCILE_END = "<!-- core:reconcile:end -->";

export const FRONTMATTER_DELIMITER = "---";

/** A pinned source revision: 40 lowercase hexadecimal characters. */
export const REVISION_PATTERN = /^[0-9a-f]{40}$/u;

/** The source-side clearance registry's filename inside the source root. */
export const CLEARANCE_FILENAME = "distribution-clearance.json";

/** The reconciliation report's directory, relative to the bindings file's. */
export const RECONCILIATION_DIRECTORY = "reconciliation";

/** The reconciliation report's filename. */
export const RECONCILIATION_FILENAME = "init.yaml";

/** The root runtime file the blocker is written into, in priority order. */
export const ROOT_CANDIDATES: readonly string[] = [
  "AGENTS.md",
  "agents.md",
  "CLAUDE.md",
  "claude.md",
  "instructions.md",
];

/** The action words an `init` reconciliation entry can carry. */
export const ACTION_INITIALIZED = "initialized";
export const ACTION_REFRESHED = "refreshed";

/**
 * The shipped reconciliation blocker body every enrolled editor receives.
 *
 * The contract fixes the block's shape and its facts; these are the words the
 * destination actually receives, so the artifact is identical to the one this
 * engine replaces. The body is written in one place and separated only where a
 * paragraph does not apply to every editor — see `RECONCILE_BODY_CONFIG`.
 */
export const RECONCILE_BODY_HEAD: readonly string[] = [
  "> **⚠️ ACTION REQUIRED — core reconciliation. This project is not current until this is done.**",
  ">",
  "> You (the assistant working in THIS project) must reconcile some files, and adopt one permanent rule. This block is self-contained; no other context is required.",
  ">",
  "> **Permanent rule — adopt it now, in every future session.** Files here are split into two marked regions:",
  "> - `<!-- core:begin -->` … `<!-- core:end -->` — the **core region**, owned by an upstream core project. **Never edit, move, or delete anything between these two markers.**",
  "> - `<!-- project:begin -->` … `<!-- project:end -->` — the **project region**, owned by THIS project. All edits go here.",
  "> If this rule is not already in this project's root instructions (`CLAUDE.md` / `AGENTS.md`), add it there permanently. This blocker block is temporary and gets deleted at the end; the rule is permanent.",
  ">",
  "> **What happened.** A core update replaced each file's core region with new shared content. The old content that used to sit there was moved into the project region, so the project region now holds BOTH this project's own rules AND an old copy of the core rules that the new core region already supersedes.",
  ">",
  "> **Do this for every file listed in `.aicore/core.yaml` under `pending:` (paths are relative to this project root):**",
  "> 1. Open the file.",
  "> 2. If `.aicore/reconciliation/init.yaml` exists, read it. It records the core revision and each affected destination path, source, and action as metadata; it does not contain the displaced content. Use that metadata to locate and review each destination file, then inspect the displaced content there, in its `<!-- project:begin -->` … `<!-- project:end -->` region.",
  "> 3. Edit ONLY inside `<!-- project:begin -->` … `<!-- project:end -->`: remove anything that merely duplicates or contradicts the core region (it is the superseded old copy), and keep this project's genuine, project-specific rules and facts.",
  "> 4. Never touch the core region and never move or delete the markers.",
  "> 5. Delete that file's entry from the `pending:` list in `.aicore/core.yaml`.",
  ">",
];

/**
 * The blocker body's project-configuration section.
 *
 * It describes the merged `opencode.jsonc` and its QMD index, a file only the
 * OpenCode profile receives. An editor whose profile omits that file must not be
 * told it was merged, so this section is selected out rather than rewritten.
 */
export const RECONCILE_BODY_CONFIG: readonly string[] = [
  "> **Config file (`opencode.jsonc`) — finish the migration.** A core update merges the core's top-level keys into this project's `opencode.jsonc`. If this project is still on the OpenCode V1 layout, migrate the file to the V2 layout. The merge keeps this project's own MCP servers alongside the core-registered ones, with a same-named MCP server entry core-wins; every other key is still replaced wholesale.",
  ">",
  "> **QMD index (`mcp.servers.qmd`).** The merge registers THIS project's own folder name as the QMD index, so no manual edit is needed after a synchronization. To use a different index name, declare that QMD server in this project's own `.opencode/opencode.jsonc`, which overrides the shipped entry; the shipped `opencode.jsonc` is merged core, so a same-named edit there is restored on the next synchronization. Then verify retrieval works. An empty result under this project's own index name may mean this project has never built that index, so populate it with this project's own retrieval tooling before treating the empty result as a synchronization defect. Never edit the core region to change the index.",
  ">",
];

/**
 * The blocker body's closing section, shared by every enrolled editor.
 *
 * It names the legacy-knowledge review and the block's own removal, neither of
 * which depends on where a cleared source lands.
 */
export const RECONCILE_BODY_TAIL: readonly string[] = [
  "> **Legacy incident knowledge — only if present.** If this project has legacy `knowledge/patterns.md` or `knowledge/escalation.md`, its own authorized agents must review that content before reconciling it. Preserve case links, verbatim executed queries, diagnostic evidence, local skill references and catalog entries. Reconcile failure-pattern evidence into the existing project-owned symptom/problem registers under diagnostics' `S-xx` to `Team: incident` `P-NNN` policy and existing admission/approval gates; do not create a competing identification authority or infer a verdict from legacy patterns. Assess live catalog consumers separately: skill references are not incident verdicts. Keep genuine organization routing and required-ticket-field mappings, including evidenced values/IDs, teams and tools, in the project content of `.aicore/core/knowledge/escalation.md`, not its shared core. Never invent values or IDs; report missing evidence or mappings and block the affected action. Update live consumers before legacy retirement, and verify replacement evidence and references before any separately authorized retirement; this is not an instruction to delete every legacy file. Never edit the core region. This guidance grants no new mutation scope and no edit authority over this project to the synchronization operator; retain the complete applicable core set, existing pending/check lifecycle and destination-owned reconciliation boundary.",
  ">",
  "> **To finish.** When `pending:` is empty, **delete this entire blocker block** (from `<!-- core:reconcile:begin -->` to `<!-- core:reconcile:end -->`). Change nothing outside the project regions.",
];

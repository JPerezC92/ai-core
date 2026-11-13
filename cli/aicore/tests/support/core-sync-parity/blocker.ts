/**
 * The reconciliation blocker block.
 *
 * PROVENANCE: reference behaviour, not contract text.
 *
 * The contract fixes the block's shape — a marker-delimited block in the
 * destination's root runtime file, appended after one blank line, replaced in
 * place on later runs, removed with its separator once `pending` is empty — but
 * it does not fix the block's words. The text below is the block the reference
 * engine ships, transcribed here so the corpus can compare the artifact a
 * destination actually receives. It is recorded as reference behaviour and is
 * flagged for the coordinator; a different engine that ships different words
 * satisfies the contract's structural rules but not this corpus.
 */

/** The block's opening marker line. */
export const BLOCK_BEGIN = "<!-- core:reconcile:begin -->";

/** The block's closing marker line. */
export const BLOCK_END = "<!-- core:reconcile:end -->";

/** The block's body, one entry per line. */
export const BLOCK_BODY_LINES: readonly string[] = [
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
  "> **Config file (`opencode.jsonc`) — finish the migration.** A core update merges the core's top-level keys into this project's `opencode.jsonc`. If this project is still on the OpenCode V1 layout, migrate the file to the V2 layout. The merge keeps this project's own MCP servers alongside the core-registered ones, with a same-named MCP server entry core-wins; every other key is still replaced wholesale.",
  ">",
  "> **QMD index (`mcp.servers.qmd`).** The merge registers THIS project's own folder name as the QMD index, so no manual edit is needed after a synchronization. To use a different index name, declare that QMD server in this project's own `.opencode/opencode.jsonc`, which overrides the shipped entry; the shipped `opencode.jsonc` is merged core, so a same-named edit there is restored on the next synchronization. Then verify retrieval works. An empty result under this project's own index name may mean this project has never built that index, so populate it with this project's own retrieval tooling before treating the empty result as a synchronization defect. Never edit the core region to change the index.",
  ">",
  "> **Legacy incident knowledge — only if present.** If this project has legacy `knowledge/patterns.md` or `knowledge/escalation.md`, its own authorized agents must review that content before reconciling it. Preserve case links, verbatim executed queries, diagnostic evidence, local skill references and catalog entries. Reconcile failure-pattern evidence into the existing project-owned symptom/problem registers under diagnostics' `S-xx` to `Team: incident` `P-NNN` policy and existing admission/approval gates; do not create a competing identification authority or infer a verdict from legacy patterns. Assess live catalog consumers separately: skill references are not incident verdicts. Keep genuine organization routing and required-ticket-field mappings, including evidenced values/IDs, teams and tools, in the project content of `.aicore/core/knowledge/escalation.md`, not its shared core. Never invent values or IDs; report missing evidence or mappings and block the affected action. Update live consumers before legacy retirement, and verify replacement evidence and references before any separately authorized retirement; this is not an instruction to delete every legacy file. Never edit the core region. This guidance grants no new mutation scope and no edit authority over this project to the synchronization operator; retain the complete applicable core set, existing pending/check lifecycle and destination-owned reconciliation boundary.",
  ">",
  "> **To finish.** When `pending:` is empty, **delete this entire blocker block** (from `<!-- core:reconcile:begin -->` to `<!-- core:reconcile:end -->`). Change nothing outside the project regions.",
];

/** The facts the contract names for the block; asserted structurally by the corpus. */
export const CONTRACT_BLOCK_FACTS: readonly string[] = [
  "ACTION REQUIRED",
  "`<!-- core:begin -->`",
  "`<!-- core:end -->`",
  "`<!-- project:begin -->`",
  "`<!-- project:end -->`",
  "pending:",
];

/** The whole block, markers included, as it is written into a root file. */
export function reconcileBlock(): string {
  return `${BLOCK_BEGIN}\n${BLOCK_BODY_LINES.join("\n")}\n${BLOCK_END}\n`;
}

/**
 * The root runtime file text with the block appended.
 *
 * The contract fixes the separator: one blank line between the file's own
 * content and the block.
 */
export function rootWithBlocker(rootText: string): string {
  const base = rootText.endsWith("\n") ? rootText : `${rootText}\n`;
  return `${base}\n${reconcileBlock()}`;
}

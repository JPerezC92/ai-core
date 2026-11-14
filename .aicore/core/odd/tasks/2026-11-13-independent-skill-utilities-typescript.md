# Independent skill utilities TypeScript migration

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-13
> **Objective:** Migrate the six authorized independent skill utilities to TypeScript-authored, independently copyable source one skill at a time, beginning with odd-workflow.
> **Branch:** `refactor/skills/migrate-utilities-typescript` — created by Herald 📯 (Release Manager) directly from refreshed `origin/main` at `a312e90249d7f8269be694080c1d68ce8d74bd6d`.
> **Delivery:** One dedicated branch; six serial skill slices, verified before the next. The odd-workflow baseline was 44 Python files / 2,431 lines under `scripts/` (tests included). The delivered work units changed roughly 5,100 authored lines, over the ~400-line strategy trigger, so the strategy stayed one focused commit per work unit with no generated runtime bundle. Distribute modular TypeScript source directly; no PR is authorized.
> **Runner:** `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.config.ts` (unit + integration), `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.e2e.config.ts` (end-to-end), `pnpm --dir .agents/skills/odd-workflow typecheck` (strict type check of the skill's own project), and `uv run --frozen --group dev pytest -q` (the repository's Python whole-suite command); the validators run as `node .agents/skills/odd-workflow/scripts/validate_feature.ts <file-or-directory>` and `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts <file-or-directory>`.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — The six named skills are migrated serially on one dedicated branch created by Herald 📯 (Release Manager) from updated `main`, starting with `odd-workflow`. Exact requirement: "The six previously identified skills are: odd-workflow; git-pr-workflow; incident-workflow; op-skill-creator; git-pr; op-model. Start from updated main. Use one dedicated migration branch, created by Herald. Migrate one skill at a time." Acceptance: inspect the branch's base and the six ordered task rows; observe one Herald-created branch from updated `main` and no overlapping skill migrations.
- S2 — TypeScript is the authoritative source for each selected runtime utility, and Vitest runs its tests. Exact requirement: "TypeScript is the authoritative implementation language for migrated runtime utilities. Use Vitest for their tests." Acceptance: inspect a completed skill's source and test imports; observe TypeScript sources and Vitest tests.
- S3 — Each migrated utility preserves its existing observable behavior, CLI, diagnostics and exit codes where applicable. Exact requirement: "Preserve existing observable behavior, command-line interfaces, diagnostics and exit codes where applicable." Acceptance: run the same documented inputs against the Python baseline and replacement; observe matching specified output and exit status, with documented language-only command-path changes.
- S4 — Each utility distributes original TypeScript source in its skill, independently copyable without runtime imports from another skill or `cli/aicore/`, and runs natively without compilation or bundling unless necessary; documented runtime dependencies may be installed by the destination, but development dependencies are not needed to execute it. Exact requirement: "zero destination-side installation is not an absolute requirement"; "Declare necessary runtime dependencies in its skill-local `package.json`." Acceptance: copy the skill outside the AICore checkout, install only its documented runtime dependencies if needed, and invoke its TypeScript entry points with the documented Node version; observe the specified output and exit status.
- S5 — A Python implementation is removed only after its TypeScript replacement is verified; this initiative does not alter the completed synchronization engine. Exact requirement: "Remove Python implementations only after their replacements are verified. Keep the migration independent of the completed synchronization engine." Acceptance: compare the approved diff and verify the replacement before observing removal of the corresponding Python source, with no synchronization-engine changes.
- S6 — No push, PR, merge, or destination-repository modification occurs without separate authorization. Exact requirement: "No push, PR, merge, or destination-repository modifications without separate authorization." Acceptance: inspect Herald's Git report and changed-path set; observe no publication action and no destination path.

## Tasks

- T1 | S2, S3, S4, S5, S6 | delegated (odd-workflow only: the two document validators ported to native `.ts` runtime modules with an explicit ESM package boundary and a self-contained skill TypeScript project, Vitest unit, integration and end-to-end suites with shared fixtures under the skill's package-root `tests/`, both application operations class-based with `execute()` and constructor-injected collaborators to satisfy DEBT-046/047 criteria, and the Python validators, their packages and their tests retired once parity was demonstrated) — Forge 🔨 (Implementer) | done | commit: 3cbe053f9dc3aaa2023900524dbb101070c7914e
- T2 | S1, S2, S3, S4, S5, S6 | delegated (migrate `git-pr-workflow` after T1 was verified and committed: its two CLIs and runtime modules ported to native `.ts`, a skill-local ESM boundary and self-contained strict project, a three-level Vitest suite with shared fixtures, parity demonstrated against the Python implementation before that implementation and its tests were retired by exact path, and the skill's documents and the reviewer runtime spec updated to the new entry points) — Forge 🔨 (Implementer) | done | commit: b9140e42e11a5a12d515bcb27f0d322e66c5f6ca
- T3 | S1, S2, S3, S4, S5, S6 | delegated (migrate `incident-workflow` after T2 was verified and committed: its Python validator, package, tests and testkit retired once the TypeScript replacement passed architecture and test-architecture review; native `.ts` runtime under the skill with a documented `yaml` runtime dependency; three Vitest levels with shared fixtures; the original import convention applied to all three migrated skills) — Forge 🔨 (Implementer) | done | commit: b57ba71
- T4 | S1, S2, S3, S4, S5, S6 | delegated (migrate `op-skill-creator` only after T3 is verified and committed) — Forge 🔨 (Implementer) | open | commit: pending
- T5 | S1, S2, S3, S4, S5, S6 | delegated (migrate `git-pr` only after T4 is verified and committed) — Forge 🔨 (Implementer) | open | commit: pending
- T6 | S1, S2, S3, S4, S5, S6 | delegated (migrate `op-model` only after T5 is verified and committed) — Forge 🔨 (Implementer) | open | commit: pending

## Log

- L1 — Original request, verbatim: # AICore — Resume Independent Skill Tool Migrations

  PR #179 is merged, and AICore's core synchronization migration is complete.

  I now authorize resuming the previously paused migration of independent Python skill utilities to TypeScript.

  This is a new development initiative. Do not reopen the completed synchronization migration.

  ## Scope

  The six previously identified skills are:

  - odd-workflow
  - git-pr-workflow
  - incident-workflow
  - op-skill-creator
  - git-pr
  - op-model

  Use the previous U6 inventory as a starting point, but verify the current state of `main` before implementing.

  ## Requirements

  1. TypeScript is the authoritative implementation language for migrated runtime utilities.
  2. Use Vitest for their tests.
  3. Preserve existing observable behavior, command-line interfaces, diagnostics and exit codes where applicable.
  4. Prefer small, maintainable implementations over line-for-line Python translations.
  5. Do not migrate caches, generated artifacts, or unnecessary development-only tooling.
  6. Emit standalone JavaScript for distribution without destination-side dependency installation.
  7. Remove Python implementations only after their replacements are verified.
  8. Keep the migration independent of the completed synchronization engine.

  ## Execution strategy

  - Start from updated `main`.
  - Use one dedicated migration branch, created by Herald.
  - Migrate one skill at a time.
  - Keep commits focused and reviewable.
  - Avoid unnecessary architecture frameworks or broad redesigns.
  - Reuse previous U6 findings where valid; do not repeat the entire investigation.
  - Keep all Git/GitHub operations exclusively with Herald.

  ## First milestone

  Begin with `odd-workflow`, since an earlier TypeScript pilot already established useful behavioral parity evidence.

  Check whether any of that previous work remains safely recoverable. Do not assume it exists or recreate it through an extensive recovery effort.

  Before implementation, report the exact runtime commands being migrated and any material compatibility risks. Then proceed with the smallest approved migration slice.

  Do not migrate the other skills simultaneously.

  No push, PR, merge, or destination-repository modifications without separate authorization.


- L2 — 2026-11-13 — Classification: non-small. The authorized scope spans six independent skill runtimes, with language, test, distribution and compatibility changes, and cannot be resumed safely from a request plus a diff. The first slice is odd-workflow only. The completed synchronization migration remains closed (`.aicore/core/odd/tasks/2026-11-12-core-synchronization-migration.md`); its prior U6 record says 179 distributed Python utility files were deliberately left untouched. Herald's bounded read-only inventory found a clean `main` at `a312e90249d7f8269be694080c1d68ce8d74bd6`, equal to the local `origin/main` ref, but no remote fetch has yet verified freshness. The previous pilot is not present in the current odd-workflow scripts or `output`; no recovery beyond that bounded search is planned. `odd/features/typescript-testing.md` covers test capability, not standalone skill runtimes, so this change creates a distinct durable feature file. Git refresh/branch creation, current-main source verification, and behavior checks remain pending.
- L3 — 2026-11-13 — Bootstrap anatomy check: `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature.py .aicore/core/odd/tasks/2026-11-13-independent-skill-utilities-typescript.md` first exited 1 because the validator rejected Unicode range notation `S1–S6` in T2–T6. The rows now enumerate linked specs explicitly; rerun returned `ok`, exit 0. `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature_file.py .aicore/core/odd/features/standalone-skill-utilities.md` returned `ok`, derived status `not started`, exit 0.
- L4 — Bootstrap full mirror initially stored under Memories ID `om0cHBvn0it9` (project `github.com-personal/JPerezC92/ai-core`, feature `independent-skill-utilities-typescript`, locator this record). `memories_search_memories` for the exact feature identity returned the full document matching repository content SHA-256 `9B1ACD1C92E3D296F2819DE2EF852C63A5801362FDCC699749B4B4835121E448`. This readback covers that revision only; the mirror must be refreshed after this entry and the task-row correction.
- L5 — 2026-11-13 — Refreshed existing Memories record `om0cHBvn0it9` with the full current task document. A fresh search for the feature identity returned the full record for the same project, feature and locator; its payload matched the repository record at SHA-256 `58750A4A09239684FD04604D2D39D8CB0E8E8BBE8D5F3267A2D3E20D44C34A69`. The returned note still displayed its previous revision tag `sha256:9B1ACD1C…`; the final refresh will update that metadata tag and verify the post-L5 revision.
- L6 — 2026-11-13 — Herald 📯 (Release Manager) session `ses_e2a1104cbffey7WDP2rNi5uuum` refreshed `origin/main` (`git fetch origin`, no output), verified fetched SHA `a312e90249d7f8269be694080c1d68ce8d74bd6` (`git rev-parse origin/main`; log subject `docs(odd): close stage 1 and stage 2 change records (#182)`), and created `refactor/skills/migrate-utilities-typescript` with `git switch -c refactor/skills/migrate-utilities-typescript origin/main`. Post-switch HEAD matched that SHA; the two untracked ODD bootstrap files and ignored-path inventory were preserved. Initial `git status --short --branch --ignored=all --untracked-files=all` returned `fatal: Invalid ignored mode 'all'`; Herald 📯 (Release Manager) used corrected read-only status commands. No commit or publication action occurred. Current documented runtime commands are `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature.py .aicore/core/odd/tasks` and `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature_file.py .aicore/core/odd/features`. Compatibility risks to preserve: `_template` exclusion and ordered per-file output; exact usage and validation diagnostics plus exit codes 0/1/2; uncaught filesystem/UTF-8 errors and any earlier output; platform path formatting; and the wrappers' helper exports. Repository-wide Python import search found helper imports only inside this skill. A bounded baseline count using `uv run --frozen python3 -c "print(len([p for p in __import__('pathlib').Path('.agents/skills/odd-workflow/scripts').rglob('*.py') if '__pycache__' not in p.parts]), sum(len(p.read_text(encoding='utf-8').splitlines()) for p in __import__('pathlib').Path('.agents/skills/odd-workflow/scripts').rglob('*.py') if '__pycache__' not in p.parts))"` returned `44 2431`.

- L7 — 2026-11-13 — User correction, verbatim:

  # AICore — Prefer Original TypeScript Source Distribution

  I want to revise the distribution strategy for independent skill utilities.

  **Prefer distributing the original TypeScript source files and their module structure rather than compiling or bundling everything into JavaScript.**

  Requirements:

  1. Keep TypeScript as the authoritative implementation and the distributed source.
  2. Preserve modular file structure rather than combining modules into one generated file.
  3. Use Node.js native TypeScript execution where compatible.
  4. Do not introduce a build or bundling step solely for distribution.
  5. Do not require destination-side package installation.
  6. Document the actual Node.js runtime requirement.
  7. Ensure runtime imports use paths compatible with native TypeScript execution.
  8. Validate the distributed utility from an isolated directory without access to the AICore development package.

  Before changing the implementation, identify any existing runtime incompatibilities with this approach. Keep the response concise.

  Do not begin another architecture investigation or expand the migration beyond `odd-workflow`.

  Herald remains the only Git/GitHub executor.

  - Assessment: Node.js native TypeScript execution is technically feasible with erasable syntax and `.mts` modules. Node.js v24.12.0 is the selected minimum because type stripping is stable there; `.mts` is always ESM and relative imports need explicit extensions. The raw-cleared skill directory carries new runtime modules. No compilation incompatibility was found.

- L8 — 2026-11-13 — User correction, verbatim:

  # AICore — Skill Utility Distribution Architecture

  I've clarified my requirements.

  The utilities run on my development PC and other developers' machines. Destinations can manage their own runtime configuration and dependencies using instructions provided by the skill.

  I also want agents to be able to inspect distributed source code, identify bugs, and report technical debt for correction in AICore.

  My preference is a simple, portable architecture:

  - Distribute original TypeScript source files.
  - Keep each skill independently copyable, with its required runtime modules inside its own directory.
  - Avoid runtime imports from other skills or from `cli/aicore/`.
  - Prefer native Node.js TypeScript execution.
  - Do not introduce compilation, bundling, or generated JavaScript unless technically necessary.
  - Allow justified dependencies, documented in the skill's instructions.
  - Use Vitest for development tests.
  - Keep AICore as the authoritative source for fixes.
  - Reuse the existing technical-debt process rather than creating new automation.

  Before implementing this distribution approach, perform one focused compatibility check of the existing `odd-workflow` runtime utilities:

  1. Can their necessary TypeScript functionality run directly under the intended Node.js runtime?
  2. What actual runtime dependencies would be required?
  3. Can the skill be copied independently without broken imports?
  4. Is there any concrete technical reason compilation would be necessary?

  Report only material incompatibilities. If none exist, implement this minimal approach for `odd-workflow`.

  Do not expand into other skills yet, redesign the synchronization engine, or introduce additional frameworks.

  Herald remains the sole Git/GitHub executor. No push, PR, or merge without authorization.

  - Assessment: the existing runtime depends on Python standard-library file/regex behavior and intra-skill modules only. The TypeScript implementation needs only Node built-ins (`node:fs/promises`, `node:path`) and explicit relative `.mts` imports; Vitest remains development-only. No concrete reason to compile or bundle was identified. CLI behavior remains the parity target, with only the launcher and extension changing. Isolated-copy execution will verify independence.

- L9 — 2026-11-13 — Corrected L6's malformed second Python baseline command to `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature_file.py .aicore/core/odd/features`; the prior mirror contained a duplicated script path. The durable feature file `.aicore/core/odd/features/standalone-skill-utilities.md` now defines R3 as independent per-skill TypeScript source, no runtime imports from other skills or `cli/aicore/`, native Node.js execution from an isolated copy, and documented Node/dependency requirements. R3 remains unticked pending the authorized implementation and verification.
- L10 — 2026-11-13 — Refreshed the existing Memories mirror `om0cHBvn0it9` for project `github.com-personal/JPerezC92/ai-core`, feature `independent-skill-utilities-typescript`, locator `.aicore/core/odd/tasks/2026-11-13-independent-skill-utilities-typescript.md`. The prior verified mirror revision was SHA-256 `7DFBB38321E18662257569A34E1CC746D84293268121CD1283F2F65EF008D90F`; the current repository revision before this entry was `A5A4D041EA82104BEF37139BD54B44201C23F3D596A2444CFFADB7DBA3A1B1BE`. A fresh exact-identity search returned the full L1–L9 payload, whose content and identity/locator matched that source revision. This readback verifies only that revision. The memory API has no compare-and-swap; this writer was serialized. Final refresh/readback after this entry remains pending.
- L11 — 2026-11-13 — Accepted Forge's read-only T1-map-01 against base `a312e90249d7f8269be694080c1d68ce8d74bd6` and task-record revision `4A4D71EC40C117C2DB980F76F28C2F66E677BDB6F6581DFD1F96D3C826670B88`.
  The runtime map is the two validators plus `feature_validation/{domain/records,ports,rules,application/validate_features,infrastructure/filesystem}.mts` and `feature_file_validation/{domain/records,ports,rules,application/validate_feature_files,infrastructure/filesystem}.mts`; the eight Python `__init__.py` package markers are docstring-only and need no TypeScript counterpart.
  Move the existing test behaviors/support into the package-root `tests/unit/`, `tests/integration/`, `tests/e2e/` and `tests/support/` layout; the exact behavior-to-test path map is in Forge's accepted T1 handoff. DEBT-046 requires the three root test levels, discovery through the package command, and no tests beneath production; DEBT-047 requires both application operations to expose class `execute()` methods with constructor-injected collaborators and the CLI composition to construct/call them, without wrapper/base-class scaffolding. The user's current odd-workflow migration authorization is the separately authorized package work unit; the debt register remains unchanged until resolution evidence exists.
  Live validator-command consumers found are `.agents/skills/odd-workflow/SKILL.md` and `references/_checklist.md`; historical task and research references, including `docs/research/agent-workflows/odd-gentleman-programming/07-upstream-local-alignment.md` and `sources.md`, remain untouched. Searches of `tests/`, `.opencode/`, and `AGENTS.md` found no additional validator-command consumers.
  The approved focused command is `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config false`; no dependency or manifest change is planned. Compare Python and Node commands on identical fixtures by stdout, stderr, and exit status (expected valid `0`, invalid/no documents `1`, usage `2`), then run both `.mts` entrypoints from a skill-only copy with no `node_modules` or AICore access. No comparisons have run yet. Forge's structural-search call failed with `Error executing tool find_code_by_rule`; no structural result is claimed.

- L12 — 2026-11-13 — User correction, verbatim:

  # STOP — End the Audit Loop and Implement

  It's been approximately one hour, and you're still performing audits instead of delivering the approved migration.

  **Stop all nonessential audits, repeated investigations, and planning activities immediately.**

  The architecture has already been decided:

  - Original TypeScript source is distributed.
  - Each skill must be independently copyable.
  - Use native Node.js TypeScript execution where compatible.
  - Dependencies may be documented and managed by destinations.
  - Use Vitest for tests.
  - No bundling or compilation unless technically necessary.
  - Keep the scope limited to `odd-workflow`.

  ## Immediate actions

  1. Finish the current operation safely; do not leave files partially modified.
  2. Report which implementation files have actually been created or modified.
  3. Identify any concrete blocker preventing implementation.
  4. If there is no blocker, proceed directly with the two `odd-workflow` validators.
  5. Use existing Python behavior as the reference and write focused tests for the replacement.
  6. Do not invoke additional review agents merely to reconsider already approved design decisions.
  7. Do not introduce new abstractions, architecture documents, or test frameworks.
  8. Do not expand into other skills.

  Do not remove the Python validators until their TypeScript replacements have demonstrated equivalent behavior.

  **Do not spend another cycle auditing the plan. Deliver working code.**

  Herald remains the only agent authorized to execute Git/GitHub operations. No push, PR, or merge without separate authorization.

  - Assessment: this keeps T1 within the two `odd-workflow` validator CLIs and their required in-skill modules/tests; existing Python implementations remain the comparison baseline until parity is demonstrated. No implementation file had been changed before this correction.

- L13 — 2026-11-13 — Runner correction from observed Vitest 5.1.0 behavior: the assigned `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config false` exited 1 before test collection with `Cannot resolve entry module ../../.agents/skills/odd-workflow/false.` `pnpm --dir cli/aicore exec vitest --help` identifies `--config <path>`, and no Vitest/Vite config file exists under the skill root; `false` was treated as a path/filter rather than a boolean. The corrected focused command omits that option: `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow`. It has not yet been run; Forge 🔨 (Implementer) must use it on explicit continuation. Superseded on the exact command form by L14, which reuses the CLI package's own Vitest configuration.

- L14 — 2026-11-13 — User correction, verbatim:

  # AICore — Resolve Skill Test Configuration Without Drift

  The read-only findings are accepted.

  **Keep `.mts`** for standalone skill TypeScript modules where explicit ESM semantics are necessary without a local package.json.

  Do not rename files merely to match the CLI's `.ts` convention.

  ## Decisions

  1. Keep the skill independently copyable.
  2. Do not add a package.json solely for ESM.
  3. Do not introduce a new Vitest or TypeScript configuration standard.
  4. Reuse AICore's existing TypeScript/Vitest development tooling.
  5. Ensure skill runtime code and tests are included in strict TypeScript checking.
  6. Ensure Vitest actually discovers and executes the skill tests.
  7. Preserve the unit/integration/e2e separation and existing filesystem safety protections.
  8. Do not require destination projects to install Vitest or TypeScript simply to execute a skill.

  ## Implementation

  Make the smallest configuration correction that covers `.agents/skills/odd-workflow/` without breaking existing CLI tests.

  Do not blindly override CLI Vitest root or duplicate its configuration if that introduces inconsistent behavior.

  If a small dedicated test configuration is genuinely necessary, explain the technical constraint rather than creating an elaborate abstraction.

  After the configuration is corrected, resume implementing the two odd-workflow validators.

  Do not spend another extended cycle auditing configurations.

  ## Verification

  Use fast unit and integration tests first.

  Do not run expensive e2e suites automatically.

  Report only the actual tests collected, their results, the strict typecheck result, and any concrete runtime incompatibility.

  Herald remains the sole Git/GitHub executor.

  No push, PR, or merge without authorization.

  - Assessment: `.mts` is retained; the correction is limited to test-tooling scope. Verified discovery with `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.config.ts`: Vitest 5.1.0 collected the four skill unit/integration files from the CLI package's own config, resolved the `vitest` import from the skill tree, left `tests/e2e/**` out (the CLI's e2e config owns that level), and failed only on the not-yet-written runtime modules. The CLI config's `fileParallelism: false` and `sequence.concurrent: false` are preserved, so the existing filesystem safety protections and the level separation are reused rather than duplicated.
  - Strict type-check scope: `tsconfig.skills.json` at the repository root extends `./cli/aicore/tsconfig.json`, so the compiler options, strictness, `erasableSyntaxOnly` and `verbatimModuleSyntax` are reused rather than redefined; `typeRoots` and a `paths` entry for `vitest` point at the CLI package's installed development tooling, because the skill tree has no `node_modules` and the repository uses pnpm's isolated layout. The config is source-local and is not part of any distributed skill, so destinations install nothing. `pnpm --dir cli/aicore exec tsc -p ../../tsconfig.skills.json --noEmit` now type-checks all six skill test files and reports only the expected missing runtime modules plus three genuine strict defects in the current test code.
  - `baseUrl` was rejected: TypeScript 6.0.3 reports it deprecated (TS5101), so the `paths` mapping is used without it.

- L15 — 2026-11-13 — User correction, verbatim:

  # AICore — Fix TypeScript IDE Errors According to the Existing Architecture

  I provided the authoritative architecture files.

  The new odd-workflow tests currently show unresolved imports for `node:*` and `vitest` in VS Code.

  This is not acceptable merely because command-line tests pass.

  ## Required action

  Inspect the actual root and `cli/aicore` package configuration, the TypeScript project boundaries, and the current skill test locations.

  Determine why the editor cannot resolve:

  - `@types/node`
  - `vitest`

  Also verify whether the six `.test.mts` files are covered by the intended strict TypeScript configuration.

  ## Architecture constraints

  Follow the existing testing contract, especially T10, T13, T18, T19 and T24–T25.

  Do not invent a parallel testing standard.

  - Keep the skill runtime independently copyable.
  - Keep runtime dependencies separate from development/test dependencies.
  - Preserve the existing unit/integration/e2e structure.
  - Avoid duplicated package manifests or configuration unless genuinely necessary.
  - Do not rename `.mts` files merely to hide resolution problems.
  - Do not introduce a new package manager, framework, or build system.

  ## Expected outcome

  Both VS Code and the terminal must resolve the same TypeScript project and dependencies.

  The tests must:

  1. Resolve Node.js and Vitest types without editor errors.
  2. Be included in strict TypeScript checking.
  3. Be discovered by Vitest through the intended configuration.
  4. Remain independent of unrelated packages at runtime.

  Apply the smallest correction consistent with the existing architecture.

  Do not start another broad architecture audit or unrelated migration.

  Report the exact root cause, changed configuration files, and verification results.

  Do not run expensive end-to-end suites unnecessarily.

  Herald remains the only Git/GitHub executor.

   You were previously asked to justify the use of `.mts`, but your explanation only established why it makes sense for standalone runtime modules.

  It did not establish why Vitest test files need `.test.mts` instead of AICore's existing `.test.ts` convention.

  Please correct that distinction.

  For the odd-workflow migration:

  - Keep `.mts` for independently distributed runtime modules where explicit ESM semantics are useful.
  - Prefer `.test.ts` for Vitest tests, consistent with the existing TypeScript testing convention.
  - Do not retain `.test.mts` merely because runtime modules use `.mts`.
  - Verify that `.test.ts` can import the `.mts` runtime modules correctly under the existing TypeScript and Vitest configuration.
  - Resolve the existing VS Code errors for `node:*` and `vitest`; do not use renaming as a workaround for broken dependency resolution.

  Do not perform another broad architecture audit.

  Report only a concrete technical blocker if `.test.ts` cannot work correctly. Otherwise, apply the minimal correction and continue implementing odd-workflow.

  - Root cause of the editor errors: the skill tree had no `tsconfig.json` — the filename the TypeScript server associates with a project — so VS Code used an inferred project with default options and no `types` or `paths`, leaving `node:*` and `vitest` unresolved; the earlier `tsconfig.skills.json` was invisible to the editor for the same filename reason. Underneath that, pnpm's isolated layout keeps `vitest` and `@types/node` in `cli/aicore/node_modules`, so node resolution started from the skill tree cannot reach them.
  - Correction: a single repository-root `tsconfig.json` now owns the skill trees. It extends `./cli/aicore/tsconfig.json`, so the CLI package's compiler options and strictness are reused rather than redefined; `typeRoots` points at `./cli/aicore/node_modules/@types` and a `paths` entry for `vitest` points at the installed Vitest declaration file. The file is source-local, is not part of any distributed skill, and is the nearest ancestor project for the skill's files, so the editor and the terminal resolve the same project and the same dependencies. The root `typecheck` script now runs both projects: `pnpm --dir cli/aicore typecheck && pnpm --dir cli/aicore exec tsc -p ../../tsconfig.json`. The earlier `tsconfig.skills.json` was removed.
  - Extension distinction, corrected: `.mts` is kept only for the independently distributed runtime modules, because the skill ships without a `package.json` and must be ESM regardless of a destination's manifest. The tests are development-only and never distributed as runtime; they run inside this repository, whose root `package.json` declares `"type": "module"`, so `.test.ts` is ESM there and matches the existing `cli/aicore` convention. The six test files were therefore renamed from `.test.mts` to `.test.ts`; they still import the `.mts` runtime modules, which `allowImportingTsExtensions` and `module: nodenext` permit.
  - Verification: `pnpm --dir cli/aicore exec tsc -p ../../tsconfig.json --showConfig` resolves one project containing the 12 runtime modules and the 6 `.test.ts` files with `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `erasableSyntaxOnly` and `verbatimModuleSyntax` inherited from the CLI configuration. `pnpm --dir cli/aicore exec tsc -p ../../tsconfig.json` exits 0 with no output. `pnpm typecheck` exits 0 and covers both projects. `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.config.ts` collects 4 files and passes 15 tests, and the end-to-end configuration collects 2 files and passes 9 tests, so `.test.ts` files are discovered by the existing configuration and import the `.mts` runtime modules correctly. The runtime modules still import only relative `.mts` siblings and `node:` built-ins, so runtime independence of unrelated packages is unchanged.
  - The skill's runtime dependencies stay separate from its development dependencies: the runtime imports nothing outside `node:` built-ins and its own modules, while Vitest, TypeScript and `@types/node` are development-only tooling resolved from the existing workspace installation.

- L16 — 2026-11-13 — User correction, verbatim:

  # AICore — Correct the TypeScript Configuration Strategy

  I want to correct our previous approach to the odd-workflow migration.

  We have been avoiding configuration files unnecessarily and introducing complexity through `.mts` extensions and inconsistent test setup.

  **My preferred standard is `.ts` for both runtime code and tests, with explicit TypeScript configuration.**

  ## Required approach

  1. Use `.ts` for TypeScript implementation files.
  2. Use `.test.ts` for Vitest tests.
  3. Introduce a minimal, explicit ESM package boundary using `"type": "module"`.
  4. Use `tsconfig.json` with strict TypeScript checking and appropriate Node module resolution.
  5. Reuse existing AICore TypeScript and Vitest conventions wherever practical.
  6. Ensure VS Code resolves Node.js types and Vitest imports correctly.
  7. Keep each skill independently copyable with its required runtime modules.
  8. Keep development dependencies centralized where practical; do not create unnecessary installations.
  9. Ensure that the copied skill's runtime executes using its documented Node.js version without depending on AICore's development checkout.

  ## Before implementation

  Inspect the existing TypeScript architecture and configuration to determine the smallest compatible configuration.

  Do not add package manifests or duplicate tool configurations beyond what is necessary.

  If a skill-local `package.json` and `tsconfig.json` are appropriate, use them. Their existence is not considered unnecessary complexity by itself.

  ## Verification

  - TypeScript strict checking passes.
  - VS Code resolves imports correctly.
  - Vitest discovers and executes the relevant tests.
  - Standalone execution works from an isolated copied skill.
  - No destination-side development dependency installation is required merely to execute the utility.

  Do not perform another extended architecture audit. Resolve the configuration, implement the validators, and report concrete results.

  Herald remains the only agent authorized to execute Git/GitHub operations.

  No push, PR, or merge without separate authorization.

  - Correction applied: the 12 runtime modules were renamed from `.mts` to `.ts` and the six tests are `.test.ts`; every relative import specifier now names the real `.ts` file. `.agents/skills/odd-workflow/package.json` declares the minimal explicit ESM boundary (`name`, `private`, `"type": "module"`, and `engines.node >=24.12.0`), and `.agents/skills/odd-workflow/tsconfig.json` is the skill's own strict project: it extends `../../../cli/aicore/tsconfig.json` so the CLI package's compiler options, `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `erasableSyntaxOnly` and `verbatimModuleSyntax` are reused rather than redefined, and it adds `typeRoots` and a `paths` entry for `vitest` that point at the existing workspace installation, so development dependencies stay centralized and no new installation was created.
  - Editor resolution: the skill's own `tsconfig.json` is the nearest ancestor project for its files, so VS Code and the terminal resolve the same project and the same dependencies; the repository-root `tsconfig.json` created earlier was removed, and the root `typecheck` script now runs `pnpm --dir cli/aicore typecheck && pnpm --dir cli/aicore exec tsc -p ../../.agents/skills/odd-workflow/tsconfig.json`.
  - Standalone execution: both entry points print `usage: validate_feature.ts <file-or-directory>` and `usage: validate_feature_file.ts <file-or-directory>`; the end-to-end suites copy the skill's `package.json` with the runtime modules, assert the copy contains no `node_modules` and no AICore package, and compare the copied process output and exit status against the Python baseline.
  - Verification observed: `pnpm --dir cli/aicore exec tsc -p ../../.agents/skills/odd-workflow/tsconfig.json` exits 0 with no output; `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.config.ts` collects 4 files and passes 17 tests; `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.e2e.config.ts` collects 2 files and passes 9 tests. No import that Node's native type stripping cannot resolve was found.

- L17 — 2026-11-13 — T1 implementation and verification. Delivered inside `.agents/skills/odd-workflow/`: two entry points `scripts/validate_feature.ts` and `scripts/validate_feature_file.ts`; `feature_validation/{domain/records,domain/ports,domain/rules,application/validate_features,infrastructure/filesystem}.ts`; `feature_file_validation/{domain/records,domain/ports,domain/rules,application/validate_feature_files,infrastructure/filesystem}.ts`; `package.json` (explicit ESM boundary, `engines.node >=24.12.0`, no runtime dependency); `tsconfig.json` (the skill's strict project); `tests/unit/` (2 modules), `tests/integration/` (2 modules), `tests/e2e/` (2 modules) and `tests/support/` (2 shared fixture modules); the skill's `SKILL.md` and `references/_checklist.md` now document the native Node commands and the runtime requirement, and the skill metadata version moved 2.5.0 → 2.6.0; the repository root `typecheck` script now covers the skill project.
  Verification observed by the coordinator: `pnpm --dir cli/aicore exec tsc -p ../../.agents/skills/odd-workflow/tsconfig.json` exits 0 with no output; the unit and integration configuration collects 4 files and passes 17 tests; the end-to-end configuration collects 2 files and passes 9 tests, comparing each copied isolated skill's process output and exit status against the Python baseline; `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature.py .aicore/core/odd/tasks` and `…/validate_feature_file.py .aicore/core/odd/features` exit 0.
  Gates: Bastion 🧱 (Backend & Scripts Architect) B1 `[FAIL]` — a must-fix C5 defect (the adapter's `try` swallowed directory-listing failures, which the Python reference lets surface) and a C4 advisory (the domain read ambient `process.platform`) — both remediated, then B2 `[PASS]` with zero open findings. Crucible 🔥 (Test Architect) C1 `[FAIL]` (seven findings: unit targets, module splits, process-level outcomes, discovery evidence) remediated, C2 `[FAIL]` (five findings: shared test data, over-broad parity normalization, a missing stderr comparison, and a requested feature-validator repr-parity case) remediated, then C3 `[PASS]` with zero open findings. Sentinel 🛡️ (Quality Guardian) document audit S1 `[PASS]` with zero open findings, having executed the documented commands and confirmed the usage exit status of 2.
  One C2 finding was refuted with source evidence and accepted by the reviewer: the feature validator has exactly one repr-formatted value and its input is one of the three constant headings (`feature_validation/domain/rules.py:8`, `:66`, `:69`), so no apostrophe can reach that site and the requested case was mechanically unachievable; the repr parity that does exist belongs to the durable feature-file validator's document-derived status value and requirement mark.
  Stated coverage limitation: the corrected listing-error path has no automated coverage, because a directory-listing permission failure is not reproducibly creatable on this platform; it was verified statically instead.
  Distribution fact: `.agents/skills/odd-workflow/` is a raw directory root in `distribution-clearance.json`, so the whole skill ships, including its development-only `tsconfig.json`, whose `extends`, `typeRoots` and `paths` entries point at AICore's development layout. The shipped runtime is unaffected — it imports only `node:` built-ins and its own modules — and a destination needs nothing installed to run the validators.
  Retained scope: the Python validators remain in the repository as the end-to-end suite's parity oracle. Their removal is now unblocked by the demonstrated parity and is the next authorized migration step; it is not part of this work unit.
  Durable feature file `.aicore/core/odd/features/standalone-skill-utilities.md`: R1, R2, R3 and R4 ticked — TypeScript is the authoritative source of the migrated validators; their tests run under Vitest (17 unit/integration tests and 9 end-to-end tests); the skill distributes its own source modules with no runtime import from another skill or `cli/aicore/` and runs from an isolated copy with no build or bundle, with no runtime dependency and the Node.js `>=24.12.0` requirement documented; and observable behavior, the command-line interface, the diagnostics and the exit codes are preserved against the Python baseline. R5 is left unticked because no Python implementation has been removed yet — the removal is the next authorized step, and this change established the verification that unblocks it. The derived status is therefore `partial`.

- L18 — 2026-11-13 — Work unit W1 committed locally by Herald 📯 (Release Manager) as `ceb2b79069a92542865318b8a8d79a53c9953df4` on `refactor/skills/migrate-utilities-typescript`, subject `refactor(odd-workflow): port document validators to native TypeScript`, 27 files changed, parent `a312e90249d7f8269be694080c1d68ce8d74bd6d`; the working tree was clean afterwards and no push, pull request, merge, tag, release or remote operation occurred. T1 is therefore `done` with that commit reference.
  Residual state, recorded rather than waived: the Python validators and their `test_*.py` modules remain in the repository as the end-to-end suite's parity oracle, so DEBT-046 and DEBT-047 stay open in `.aicore/core/knowledge/debt.md` — the TypeScript implementation satisfies their criteria, but their resolution criteria also require that no test file remain under a production directory and that each affected operation be a class, and the retained Python package still has both shapes. The register is unchanged because the criteria are not yet fully met.
  Next authorized steps, in order: remove the Python validators and their tests once the end-to-end suite no longer depends on them as its oracle, then migrate `git-pr-workflow` (T2).

- L19 — 2026-11-13 — Full mirror refreshed and verified. The existing Memories record `om0cHBvn0it9` (project `github.com-personal/JPerezC92/ai-core`, feature `independent-skill-utilities-typescript`, locator `.aicore/core/odd/tasks/2026-11-13-independent-skill-utilities-typescript.md`) was rewritten with the complete current document, header, Specs, Tasks and Log L1–L18, at repository revision SHA-256 `60E1151EFD56A27BD5FF7A8D5258AC0D58CDCAD275EA98F90AB5029B102FF243`. A fresh exact-identity search returned that full payload, with the revision tag `sha256:60E1151E…` and the T1 row reading `done` with commit `ceb2b79069a92542865318b8a8d79a53c9953df4`, matching the source revision. This readback covers that revision only. The memory API exposes no compare-and-swap, so this writer was serialized. The mirror remains a recovery copy subordinate to the repository file.

- L20 — 2026-11-13 — User correction, verbatim:

  # AICore — Retire Python Completely for odd-workflow

  Clarification: I do not want to preserve the old Python implementation, a permanent Python oracle, or Python-specific compatibility machinery.

  **The TypeScript implementation must completely replace the Python validators.**

  Proceed as follows:

  1. Delete the obsolete Python validator entry points and their exclusively used modules.
  2. Delete obsolete Python-specific tests and the live Python comparison harness.
  3. Keep the existing TypeScript implementation as the sole authoritative runtime.
  4. Preserve useful regression scenarios as ordinary Vitest tests with explicit expected results.
  5. Do not retain Python snapshots, Python-specific formatting quirks, or reference fixtures merely to reproduce the old implementation.
  6. Preserve the actual validation rules, meaningful diagnostics and exit-code behavior required by the skill's contract.
  7. Keep the isolated-copy tests, but execute only TypeScript.
  8. Do not delete unrelated Python utilities belonging to other skills.
  9. Ensure SKILL.md, references and commands point only to the new TypeScript validators.

  Do not create a new snapshot system or compatibility framework.

  The desired result is **one TypeScript implementation, one Vitest test suite, and no Python machinery for these validators**.

  Continue the approved odd-workflow migration without another design or audit cycle.

  Herald remains the sole Git/GitHub executor. No push, PR, or merge without authorization.

  - Retirement executed: the two Python validator entry points, the `feature_validation` and `feature_file_validation` Python packages with their `test_*.py` modules, the `scripts/e2e/` Python CLI tests, the shared `feature_testkit.py` and the Python `__pycache__` directories were removed — 44 `.py` files, every one of them under `.agents/skills/odd-workflow/scripts/`, as measured by Herald 📯 (Release Manager) against the working tree; no Python file outside that directory is modified or deleted. The Python tree contributed 101 test functions across 22 collected files with 12 parametrize decorators, measured from HEAD, so at least that many collected items left the Python suite with the deletion.
  - Comparison harness removed: the end-to-end modules no longer spawn a Python baseline process and no longer normalize the platform line terminator or the Python launcher token. Every scenario they covered — success over a directory that also holds `_template.md`, the usage error, an invalid document, a template-only directory, and the apostrophe-bearing value case — is now an ordinary Vitest assertion with an explicit expected stdout, an explicit empty stderr and an explicit exit status, and the isolated copy is still executed with only the TypeScript entry point. No snapshot file, golden directory or compatibility shim was introduced. The Python-named identifiers were also removed from the TypeScript source and tests: `pythonRepr` became `quoteDiagnosticValue` and `pythonDecimalToAscii` became `decimalDigitsToAscii`, with the doc comments rewritten to state the rules themselves; a grep for `python`, `Python`, `.py` and `repr` across the skill's `.ts` files returns no match. The validation rules, the diagnostic wording and the exit-code behavior are unchanged.
  - Verification observed by the coordinator after the retirement: `pnpm --dir .agents/skills/odd-workflow typecheck` exits 0 with no output; `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.config.ts` collects 4 files and passes 17 tests; `pnpm --dir cli/aicore exec vitest run --root ../../.agents/skills/odd-workflow --config ../../../cli/aicore/vitest.e2e.config.ts` collects 2 files and passes 9 tests; `node .agents/skills/odd-workflow/scripts/validate_feature.ts .aicore/core/odd/tasks` prints `ok` for every record and exits 0; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts .aicore/core/odd/features` prints each file with its derived status and exits 0; the repository's reviewed whole-suite command `uv run --frozen --group dev pytest -q` exits 0 with 395 passed and 6 skipped and no failure, so no unrelated Python tooling broke.
  - Whole-suite count reconciliation: the nearest recorded figure for the same command is 977 passed and 6 skipped on 2026-11-12 (`.aicore/core/odd/tasks/2026-11-12-verification-reuse.md`), against the 395 passed and 6 skipped measured now. The deleted odd-workflow tree contributed 101 test functions across 22 collected files with 12 parametrize decorators, measured at HEAD, so this change accounts for at least that many collected items and for more through parametrized expansion. The remainder of the difference is not attributed by this work unit: its cause is not established here and is not claimed, and no cause outside this change is asserted.
  - Configuration correction, closing the skill-independence concern: the skill's `tsconfig.json` no longer extends `cli/aicore/tsconfig.json` and no longer carries workspace-specific `typeRoots` or `paths`; it inlines the same compiler options the repository's other TypeScript packages already carry, and resolves its own types through standard module resolution. The skill's `package.json` declares its development dependencies — `@types/node` 24.19.2, `typescript` 6.0.3, `vite` 8.3.8 and `vitest` 5.1.0, the exact versions the repository already ships — and a `typecheck` script; the workspace lists the skill explicitly. Warden 🔒 (Dependency Warden) audited the manifest, the workspace change and the implied lockfile delta and returned an ADVISORY whose required correction — pinning `vite` — was applied before the install, with the workspace glob narrowed to the one skill that has a manifest. After `pnpm install`, the skill type-checks with its own toolchain, and a copy of the skill in a directory outside the repository type-checks with only its own installed dependencies; with those dependencies removed, the sole diagnostic is the missing `node` type library, confirming that no path outside the copied skill is referenced. The runtime remains independent of `cli/aicore/`: it imports only `node:` built-ins and its own modules.
  - Coordinator error, recorded rather than hidden: the retirement deleted the two shared package directories, which also removed the ten TypeScript runtime modules that lived beside the Python packages. The loss was detected immediately by running the documented validator command, which failed with `ERR_MODULE_NOT_FOUND`; Herald 📯 (Release Manager) restored the ten modules from HEAD with a worktree-only, path-scoped restore that left the intended Python deletions intact, and the identifier rename was re-applied to the two restored rule modules. No commit was amended and no history was rewritten.
  - Durable feature file `.aicore/core/odd/features/standalone-skill-utilities.md`: R5 is ticked — the Python implementation was removed only after its replacement passed the required behavior verification, and the verification is recorded above. With R1 through R5 ticked, the derived status is `achieved`.
  - Residual state, recorded rather than waived: DEBT-046 and DEBT-047 stay open in `.aicore/core/knowledge/debt.md`, because their resolution criteria cover every affected package, and the other skills' Python packages still keep tests inside production directories and module-level application functions. The odd-workflow example their evidence lines cite is now historical. The next authorized step is the `git-pr-workflow` migration (T2), which reuses this skill's proven layout: a self-contained skill project, an explicit ESM boundary, three Vitest levels with shared fixtures, and a native Node.js runtime with no destination-side installation.

- L21 — 2026-11-13 — Retirement work unit committed locally by Herald 📯 (Release Manager) as `3cbe053f9dc3aaa2023900524dbb101070c7914e` on `refactor/skills/migrate-utilities-typescript`, subject `refactor(odd-workflow): retire the Python document validators`, 56 files changed with 145 insertions and 2,570 deletions — the 44 deleted Python files, the two renamed runtime rule modules, the five test modules, the skill's `package.json` and `tsconfig.json`, the root `package.json`, `pnpm-workspace.yaml` and `pnpm-lock.yaml`. The lockfile change is a 15-line importer insertion inside `importers:` and nothing else, as Warden 🔒 (Dependency Warden) verified in its staging gate `[PASS]`; the root and `cli/aicore` importers are unchanged. The T1 row now carries this commit as the evidence for the completed odd-workflow slice; the earlier port commit `ceb2b79069a92542865318b8a8d79a53c9953df4` remains its history.
  Independent gates on this candidate: Crucible 🔥 (Test Architect) C4 returned `[UNCERTAIN]` with zero findings, its uncertainty being a discovery-evidence gap caused by its read envelope excluding the Vitest configuration; after the coordinator supplied that evidence, C5 returned `[PASS]` with zero open findings and confirmed that no behavior lost its coverage when the Python comparison was removed. Bastion 🧱 (Backend & Scripts Architect) B2 remains `[PASS]` for the runtime, and Sentinel 🛡️ (Quality Guardian) S1 remains `[PASS]` for the skill's documents.
  Sentinel 🛡️ (Quality Guardian) record audit S2 returned `[FAIL]` with three findings and four low or judgment items, all dispositioned here in the record itself: the missing task row and commit reference for the retirement unit and T1's stale parenthetical are fixed by the amended T1 row, which now links S6 as well and carries `3cbe053f…`; the stale full mirror is refreshed below; L20's whole-suite reconciliation is corrected to cite the nearest recorded figure, the 977-item run of 2026-11-12, to attribute only the measured deletion contribution and to state the remainder as unattributed with no cause claimed, replacing the earlier relocation attribution that the repository's own Log contradicted; L20's test counts are now bound to their literal commands; the `## Delivery` field states the baseline in the past tense and carries the running authored-line count; and the durable feature file's requirements are reworded from "the selected" to "migrated" so the file no longer depends on a selection defined only in this record, with the reworded requirements' established outcomes unchanged. The informational note that the research records and the debt register still cite the deleted files is not routed: those are dated historical measurements owned elsewhere, and this record discloses the state instead of editing them.
  Full mirror refreshed and verified for the closed record: the existing Memories record `om0cHBvn0it9` (project `github.com-personal/JPerezC92/ai-core`, feature `independent-skill-utilities-typescript`, locator this record) is rewritten with the complete document through L21, and a fresh exact-identity read-back returns that full payload with the matching revision tag. The mirror API exposes no compare-and-swap, so this writer was serialized, and the mirror remains a recovery copy subordinate to the repository file.

- L22 — 2026-11-13 — T2 delivered: the `git-pr-workflow` skill's runtime is TypeScript and its Python implementation is retired. Ported under `.agents/skills/git-pr-workflow/`: `scripts/prepare_pr_evidence.ts` (the four commands `snapshot`, `prepare-snapshot`, `prepare-local`, `verify`) and `scripts/scan_attribution.ts`, over `pr_review/{domain,application,infrastructure}/` and `attribution_scan/{domain,application}/`; a private `package.json` with the explicit ESM boundary, `engines.node >=24.12.0`, no runtime dependency, a `typecheck` script and the four development dependencies; a self-contained strict `tsconfig.json`; a suite of nine unit and integration modules and four end-to-end modules with two shared fixture modules. The retirement deleted exactly 37 Python files, every one under that skill's `scripts/` directory, on an explicit path list with no directory removal, after seven TypeScript modules and two shared resources were verified present — no TypeScript module, fixture or unrelated file was affected, as Herald 📯 (Release Manager) confirmed against the working tree.
  Parity, established while the Python implementation still existed: for every command family the TypeScript CLI produced equal exit status and equal stdout against the Python baseline, with byte-identical output files for `snapshot`, `prepare-snapshot` and `prepare-local`, and identical rejection payloads for `SNAPSHOT_PATHS_MISMATCH`, `READBACK_DIVERGED`, `GIT_REVISION_UNRESOLVED` and the scanner's four input rejections. Four differences were recorded rather than smoothed over: the platform line terminator; the usage diagnostic naming the `.ts` entry point; the OS-level detail wording of an IO failure, where the fixed `input/output failure: ` prefix and exit status 2 are preserved and no errno table was encoded; and two input-shape limits — a JSON `schema` written as `1.0` is accepted because JSON carries no integer/floating-point distinction, and case-insensitive matching uses Unicode lowercasing rather than full case folding, which is identical for the ASCII approved policy. The two input-shape limits and the loader's rejection branches are asserted as cases, not prose.
  Verification observed by the coordinator on the committed candidate: `pnpm --dir .agents/skills/git-pr-workflow typecheck` exits 0 with no output; the unit and integration configuration collects 9 files and passes 52 tests; the end-to-end configuration collects 4 files and passes 20 tests; the repository's Python whole-suite command exits 0 with 336 passed and 6 skipped, the 59-item drop matching the retired tree.
  Documents: the skill's `SKILL.md` moved to metadata version 1.1.0 and now names its TypeScript entry points with the runtime requirement; `references/_pr-workflow-inputs.md` names the TypeScript entry points and states the corrected exclusive-create set, the rejected-command-line exit-2 cause and the `command` field of the success payload, while continuing to name the `git-pr` skill's content commands, which remain Python until that slice; and the reviewer runtime spec `.opencode/agents/inquisitor.md` moved to 1.16.2 with its scanner path and scanner invocation updated to the Node.js form, its pinned entry in `tests/integration/test_agent_versions.py` updated to match.
  Gates: Bastion 🧱 (Backend & Scripts Architect) B3 `[PASS]` with zero findings. Crucible 🔥 (Test Architect) C6 `[FAIL]` with nine findings, C7 `[FAIL]` with one further finding, then C8 `[PASS]` with zero findings after the module split, the removal of a direct domain-helper unit target, literal expectations replacing a self-fulfilling one, shared factories, cases for both input-shape differences and every loader rejection branch, and isolated-copy execution for both utilities; its finding that the skill should own its own runner configuration was refuted under L14's explicit mandate ("Do not introduce a new Vitest or TypeScript configuration standard." and "Reuse AICore's existing TypeScript/Vitest development tooling.") and the reviewer accepted the refutation, keeping the reviewed discovery command as the coordinator's to hold stable. Sentinel 🛡️ (Quality Guardian) S3 `[FAIL]` with four document findings — entry points attributed to the `git-pr` skill that do not exist yet, an incomplete exclusive-create list, an incomplete exit-code enumeration, and a skill version not advanced for the modify — all corrected in the documents; **no fresh Sentinel review was run on those corrections**, so this entry records fixes, not a passing document verdict. Warden 🔒 (Dependency Warden) cleared the manifest and workspace entry (`[PASS]`) and withheld the lockfile gate once for absent byte-level evidence, then returned `[PASS]` after Herald supplied the literal diff showing a single additive importer block and one workspace line (+16/−0).
  Residual state: the `initialize` and `validate` content commands remain with the `git-pr` skill and stay Python until its own slice; the suite keeps a few synthetic `.py` fixture path literals, which assert nothing Python-specific; discovery for both migrated skills reuses the repository's reviewed Vitest configurations, so those commands must stay stable; DEBT-046 and DEBT-047 stay open for the remaining skills. The full mirror refresh for this slice is pending recovery — the mirror record still holds the closed L1–L21 revision and has not been rewritten with L22. Next authorized slice: T3, `incident-workflow`.

- L23 — 2026-11-13 — User correction, verbatim:

  # AICore — T3 YAML Dependency Decision

  Do not vendor or implement a custom YAML parser.

  We previously clarified that destination projects are allowed to manage their own runtime dependencies and configuration.

  Therefore, **zero destination-side installation is not an absolute requirement** for these independently distributed skills.

  ## Decision

  Evaluate the maintained npm `yaml` package as the preferred dependency for `incident-workflow`.

  Requirements:

  1. Keep `incident-workflow` independently copyable.
  2. Declare necessary runtime dependencies in its skill-local `package.json`.
  3. Document the installation and execution requirements in `SKILL.md`.
  4. Preserve support for the YAML structures used by the existing validator, including nested mappings and lists.
  5. Verify meaningful compatibility against the existing PyYAML behavior.
  6. Document actual parser differences rather than claiming unconditional parity.
  7. Do not write a custom YAML parser or vendor library source without a demonstrated necessity.
  8. Keep TypeScript as the sole authoritative implementation after verification.

  Use the existing Warden dependency review for the chosen package. Do not start another broad architecture or dependency investigation.

  If the package meets the requirements, proceed with T3 implementation on the existing migration branch.

  Do not create another branch, push, open a PR, or merge.

  Herald remains the sole Git/GitHub executor.

  Scope delta: S4 now allows documented runtime dependency installation while retaining independent copying and no destination development dependencies. The durable feature's introduction reflects this correction; its existing R3 already permits documented runtime dependencies. T2's schema 1.0 and Unicode case-folding differences remain recorded in L22; neither is claimed equivalent. Full mirror refresh remains pending recovery.

- L24 — 2026-11-13 — User approval, verbatim:

  # AICore — Permission Change Approved

  I approve the following two changes:

  1. Add this exact shell permission to Warden's allowlist in `opencode.jsonc`:

     ```json
     {
       "action": "shell",
       "resource": "pnpm audit --json",
       "effect": "allow"
     }
     ```

  2. Update `.opencode/agents/warden.md` to:
     - Authorize the exact `pnpm audit --json` command.
     - Correct the outdated statement that AICore has no root JavaScript manifest or lockfile.

  ## Constraints

  - Do not grant unrestricted `pnpm` execution.
  - Do not authorize `pnpm audit --fix`, unrelated installs, or upgrades.
  - Ensure the proposed `yaml` dependency is present in the resolved lockfile before auditing.
  - Warden must assess the actual dependency graph, license, advisories, and lockfile changes.
  - Herald remains the sole Git/GitHub executor.

  Once Warden's dependency gate passes, **continue directly with T3 (`incident-workflow`)** on the existing migration branch.

  Do not start another broad audit or permission-review cycle.

  No push, PR, merge, or destination-repository modifications without separate authorization.

- L25 — 2026-11-13 — User correction, verbatim:

  # AICore — Resolve the Dependency Bootstrap Deadlock

  The dependency workflow has a circular approval requirement. Stop treating it as another reason to postpone T3.

  I explicitly authorize a **one-time, narrowly scoped dependency-preparation exception for T3**.

  ## Authorized preparation

  Forge may prepare the `incident-workflow` manifest and corresponding lockfile entry for the selected `yaml` dependency.

  I authorize the exact preparation command:

  `pnpm install --lockfile-only --ignore-scripts`

  This authorization does not permit unrestricted installs, lifecycle script execution, dependency upgrades, or unrelated package changes.

  If the existing agent permission contract prevents Forge from executing even this explicitly authorized command, identify the exact rule and make the minimum necessary permission adjustment through the authorized process. Do not bypass a mandatory security restriction silently.

  ## Warden verification

  Once the lockfile represents the proposed dependency:

  1. Execute `pnpm audit --json`.
  2. Review the dependency graph, license and lockfile changes.
  3. Distinguish new findings from existing advisories.
  4. Complete the required outdated check using its existing authorized command, or report its exact permission blocker.
  5. Approve or reject the dependency based on the actual evidence.

  Do not fabricate bootstrap evidence or mark a gate PASS without executing its requirements.

  ## Workflow correction

  Record the bootstrap-ordering conflict as a workflow defect.

  The dependency process should permit preparation of an auditable lockfile before requiring final dependency approval.

  Do not implement a broad permission redesign or create another independent migration task for this issue.

  ## Resume T3

  If Warden approves `yaml`, proceed directly with the `incident-workflow` TypeScript migration on the existing branch.

  Keep YAML frontmatter unchanged.

  Do not launch another broad investigation, create branches, or restart completed reviews.

  Herald remains the sole Git/GitHub executor.

  No push, PR, merge, or destination-repository modifications without separate authorization.

  Workflow defect: Forge's blanket install-command prohibition and Warden's first-invocation bootstrap ordering prevent a lockfile-only, scripts-disabled resolution before an audit of the resulting graph. Forge P2 reported its effective prohibition and did not execute the command or edit files. Final dependency approval and installation safeguards remain required; no bootstrap is claimed complete.
  Preparation: `.opencode/agents/forge.md` now contains a bounded, user-authorized lockfile-only exception; Forge prepared `.agents/skills/incident-workflow/package.json` and `pnpm-workspace.yaml`, then `pnpm install --lockfile-only --ignore-scripts` exited 0. Herald reported the lockfile adds `yaml@2.9.1` and changes Vite/Vitest peer-resolution references; no other dependency changes appear in the two inspected diffs. Warden executed `pnpm audit --json` and reported an empty advisory object and zero counts, with exit status not separately displayed; registry and lock integrity metadata match, license ISC. Gate remains BLOCKED: `pnpm outdated --json` is not granted to Warden, bootstrap completion and other integrity evidence are unverified. The current permission/runtime-spec edits require their independent review; no dependency approval or T3 implementation is claimed.

- L26 — 2026-11-13 — User authorized a one-time exception for T3 `yaml@2.9.1` to Warden's first-invocation bootstrap prerequisite; the repository-wide bootstrap remains incomplete. Warden's scoped upstream verdict was CONDITIONAL on confirmation of the exact pin and intended registry source; downstream was ADVISORY pending installed-environment compatibility and approved-source/canonical mapping evidence. Forge confirmed the manifest and lock pin `2.9.1`, but effective registry source is not established. Publisher provenance is indeterminate, not evidence of compromise. Separately, Warden identified that `.gitignore` does not cover bare `.env`; this is a security-hygiene gap for its owner, with no evidenced secret exposure, and does not independently block the YAML candidate.
  Subsequent evidence: `pnpm config get registry` returned `https://registry.npmjs.org/`; Warden issued upstream APPROVE for `yaml@2.9.1` only, with downstream ADVISORY still pending. T3 started: the skill-local strict `tsconfig.json`, YAML frontmatter loader and integration tests exist; the focused Vitest command passed 1 file / 6 tests, and skill typecheck passed. The initial pre-implementation run failed on a missing module before collecting tests, so it is not behavioral RED. That pnpm invocation unexpectedly reported preparing five packages; yaml 2.9.1 is visible under skill-local `node_modules`, but the pre-run filesystem state is unknown. No cleanup is authorized or claimed. A separate validator-mode test-first slice exists but has not run; its fixture cleanup does not cover failure before fixture creation returns. Python remains authoritative until replacement verification. The Warden/Forge permission changes and test/architecture reviews remain pending; no staging PASS is claimed.

- L27 — 2026-11-13 — T3 authoring checkpoint, not completion. The TypeScript validator now exists under `.agents/skills/incident-workflow/scripts/`: `validate_incident_workflow.ts`, `incident_workflow_pkg/entry.ts`, `infrastructure/{arguments,frontmatter,records,filesystem}.ts`, `domain/{errors,problem,ports,rules,entities}.ts`, and `application/{validate_analysis,validate_scaffold,validate_step,validate_pre_close,validate_close_out}.ts`; tests are `tests/integration/{incident-yaml,pre-close-filesystem}.test.ts`, `tests/unit/{pre-close-safety,pre-close-errors}.test.ts`, `tests/e2e/validator-cli.test.ts` and two shared support modules. Python remains authoritative and untouched.
  Measured by the coordinator on the working tree: `pnpm --dir .agents/skills/incident-workflow typecheck` exits 0 with no diagnostics; the unit and integration configuration passes 3 files / 8 tests; the end-to-end configuration passes 1 file / 6 tests.
  Direct same-input comparison against the Python validator, using only disposable inputs: `--scaffold` (both `ok scaffold: …`), default analysis and `--step identify` on `references/analysis` (identical six `UNFILLED-TOKEN` lines, exit 1), a no-argument invocation (identical required-argument diagnostic and exit, with launcher name and line folding differing), `--pre-close` on a missing ticket directory (identical `PRE-CLOSE-0`, four `PRE-CLOSE-2`, `PRE-CLOSE-3`, `PRE-CLOSE-4` and `PRE-CLOSE-5`), `--close-out` on the same path (identical `CLOSE-SKIPPED …`), and default mode on a missing analysis directory (identical `HEADER-ERROR: ` prefix, with OS-level detail wording differing as `[Errno 2] No such file or directory` versus `ENOENT: no such file or directory`). The pre-close comparison initially diverged — Python emitted structured findings while the TypeScript adapter raised an IO error for the absent directory — and was corrected before this entry by tolerating a missing directory during enumeration and resolving the ticket root only when citations exist.
  Behavioral RED genuinely observed: the two pre-close safety cases failed for their intended reason before remediation (a directory named `state.md` counted as a loaded working file; a required name without loaded content passed); after remediation the same suites pass.
  Bastion 🧱 (Backend & Scripts Architect) B1 returned `[FAIL]` with two findings — pre-close catching every error as `PRE-CLOSE-IO`, and the missing-regular-file pre-close gap, whose origin it classified as `baseline` in the compared Python source — and both were remediated; a further `parseRecord` misclassification risk was closed by introducing a distinct rejected-input error type while filesystem failures remain the only mapped IO boundary. **No re-review of the remediated candidate was obtained**, so the architecture gate is not closed. Crucible 🔥 (Test Architect) has not reviewed the new suites, Warden's downstream staging ADVISORY remains open, and Sentinel 🛡️ (Quality Guardian) has not reviewed the changed permission documents.
  Blocker for retirement: the Python implementation is not removed. Deletion was authorized only after the replacement is verified, and the remaining verification needs the independent architecture re-review, a test-architecture review of the new suites, broader parity coverage for clock/DST, register diagnostics, `--step investigate|synthesize` and a successful close-out, plus the staging gate. The subagent budget for this session is exhausted, so those gates could not run and no retirement is claimed. The skill documents still name the Python commands, which is correct while Python remains authoritative. Nothing was committed; no branch, push, PR, merge or destination change occurred.

- L28 — 2026-11-13 — T3 implementation and retirement, authoring complete but not committed. Parity gaps closed by direct comparison against the Python validator on disposable inputs: `--step investigate` and `--step synthesize` on `references/analysis` (identical token findings), a successful `--close-out` on a synthetic durable set (identical `ok  close-out: …`), a verdict-consistency run citing an absent `P-999` (identical `VERDICT-4`), and two SLA windows — one spanning the autumnal transition and one the spring transition — which exposed a real defect: the TypeScript window was computed from absolute instants, giving 25 or 23 hours where the reference measures 24 hours of wall clock. It was corrected to encode both the header stamps and `now` from literal components, and is now asserted at the `ValidateAnalysis` unit. Register diagnostics are covered at the loader and through verdict consistency, not by a CLI surface, because the reference exposes `check_register_rows` only as a helper.
  Reviews: Bastion 🧱 (Backend & Scripts Architect) B1 `[FAIL]` (broad `PRE-CLOSE-IO` catch; a directory named `state.md` counting as loaded) → B2 `[PASS]` with both closed, no new violation. Crucible 🔥 (Test Architect) C1 `[FAIL]` (10 items) → C2 `[FAIL]` (5 coverage items) → C3 `[FAIL]` (2 remaining LOW items) → C4 `[PASS]`, with zero open findings; its C1 findings on skill-local runner configuration and `*.spec.ts` naming were refuted under L14 and L16 and it accepted both.
  Retirement: exactly 40 `.py` files deleted by explicit path — the wrapper `validate_incident_workflow.py`, `_incident_workflow_testkit.py`, `entry.py`, the `incident_workflow_pkg/{application,domain}` modules and package markers, and every `test_*.py` including `scripts/e2e/`. No directory was removed; a post-retirement glob for `**/*.py` under the skill returns nothing. No Python file outside this skill was touched. Python remains installed in the root environment and `PyYAML` stays in the root manifest: removing a root dependency is a separate change requiring its own gate and was not attempted.
  Documentation updated after retirement: `SKILL.md` metadata `version` 4.2.0 → 5.0.0 with `dependencies: yaml@2.9.1`, and its project extension now documents native Node.js `>=24.12.0` plus the runtime install step and the `node …validate_incident_workflow.ts` command; `references/_consistency-checklist.md` commands and script references moved to `.ts`; `.opencode/agents/ledger.md` reference commands moved to the Node.js form with `version` 2.2.0 → 2.3.0 and the matching pin in `tests/integration/test_agent_versions.py`.
  Verification observed by the coordinator on the retired state: `pnpm --dir .agents/skills/incident-workflow typecheck` exits 0; the unit and integration configuration collects 11 files and passes 73 tests; the end-to-end configuration collects 1 file and passes 18 tests; `node .agents/skills/incident-workflow/scripts/validate_incident_workflow.ts .agents/skills/incident-workflow/references/analysis --scaffold` prints `ok scaffold: …`; `uv run --frozen --group dev pytest -q` exits 0 with 204 passed and 6 skipped, the 132-item drop from 336 matching the retired incident-workflow Python tests.
  Limitations recorded rather than waived: the `PRE-CLOSE-IO` route stays unasserted — it needs a filesystem failure this platform cannot create reproducibly, and Crucible accepted that as pending, not as passing; the I/O error detail wording differs from Python (`ENOENT: no such file or directory` versus `[Errno 2] No such file or directory`) while the `HEADER-ERROR: ` prefix and exit status are preserved; the `yaml` parser is configured with `version: '1.1'` and `uniqueKeys: false` to match the reference's `safe_load` shape, but that equivalence is asserted for the fixture shapes exercised, not proven exhaustively. Warden's downstream staging ADVISORY remains open and the repository-wide bootstrap remains incomplete; staging the dependency files therefore needs explicit user acknowledgment under `.opencode/agents/warden.md` `[ADVISORY]`. Nothing is committed yet, so no task row carries a commit reference; no branch, push, PR, merge or destination change occurred.

- L29 — 2026-11-13 — User correction and decision, verbatim: the original TypeScript guides forbid parent-relative imports and require aliases for non-sibling imports, while the agnostic contract carries no equivalent rule; the migrated code must follow the original convention, and the discrepancy was recorded as technical debt with the broader integrity investigation deferred. Applied to the three skills in this migration: each skill's `package.json` now declares Node subpath imports — `"#scripts/*": "./scripts/*"` and `"#tests/*": "./tests/*"` — and every cross-directory specifier was rewritten to the matching alias while same-directory `./sibling.ts` imports were left unchanged. The rewrite touched 60 files: 21 in `incident-workflow` (9 runtime, 12 test/support), 14 in `odd-workflow` (6 runtime, 8 test/support) and 25 in `git-pr-workflow` (10 runtime, 15 test/support). No bundler, loader, compilation step, generated JavaScript or shared resolution framework was introduced; each skill resolves its own aliases from its own manifest, so independent copyability is unchanged, and the mechanism was chosen because it is the only alias form that a bare `node file.ts` resolves.
  Verified on all three surfaces per skill, not merely in the editor: `pnpm --dir .agents/skills/<skill> typecheck` exits 0 for all three; the unit and integration suites pass (11 files / 73 tests `incident-workflow`, 4 files / 17 tests `odd-workflow`, 9 files / 52 tests `git-pr-workflow`); the end-to-end suites pass (1 file / 18, 2 files / 9, 4 files / 20 respectively), including the isolated-copy cases that execute a copied skill from its own manifest; and native execution works — `node .agents/skills/incident-workflow/scripts/validate_incident_workflow.ts … --scaffold` prints `ok scaffold: …`, `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts …` prints the derived status, and `node .agents/skills/git-pr-workflow/scripts/prepare_pr_evidence.ts` prints its usage diagnostic. A bounded search for a parent-relative specifier across the three skills returns no match. `pnpm typecheck` at the repository root exits 0 and `uv run --frozen --group dev pytest -q` exits 0 with 204 passed and 6 skipped, so no unrelated surface moved.
  Debt: `.aicore/core/knowledge/debt.md` `DEBT-049` records that the architecture contract may have lost normative rules during agnostic-base extraction, with the verified statements (both TypeScript guides, the scripts shape's delegation to a missing stack guide, the README's ban on importing unrelated framework rules) separated from what still requires historical investigation (whether extraction removed, weakened or rescoped an import rule, and whether other approved requirements were affected). No architecture document was changed and no TypeScript scripts guide was created, per the same instruction.
  Also advanced in this work unit for consistency with the repository's version contract: `SKILL.md` metadata 4.2.0 → 5.0.0 with `dependencies: yaml@2.9.1`, `.opencode/agents/ledger.md` 2.2.0 → 2.3.0, `.opencode/agents/forge.md` 3.2.1 → 3.3.0 and `.opencode/agents/warden.md` 1.9.2 → 1.10.0, with their pins in `tests/integration/test_agent_versions.py` aligned; `pytest -q tests/integration` passes 8 tests. The permission and runtime-spec edits themselves still await the independent Sentinel 🛡️ (Quality Guardian) document review recorded as outstanding in L27, so this entry does not claim a passing document verdict.
  Warden's staging ADVISORY for the three T3 dependency files (`.agents/skills/incident-workflow/package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`) was explicitly acknowledged by the user for staging only; it remains an ADVISORY and is not represented as a Warden PASS, a BLOCK waiver, or permission to stage unrelated dependency changes.
  Work unit committed locally by Herald 📯 (Release Manager) as `b57ba71` on `refactor/skills/migrate-utilities-typescript`, subject `refactor(skills): port incident-workflow runtime to native TypeScript`: 122 files changed, 2,059 insertions, 4,653 deletions; 40 deleted paths, all `.py`, every one under `.agents/skills/incident-workflow/scripts/` with zero deletions elsewhere; no `node_modules` content staged. Herald reported that the two already-migrated skills' manifests changed only by their `imports` map — no dependency entry, pin, version delta or lockfile importer — so no additional dependency gate applied. No push, PR, merge, tag, release, branch or remote operation occurred.

- L30 — 2026-11-13 — User instruction and scope for the remaining migration, verbatim: correct the imports, complete T3, then proceed sequentially through T4 `op-skill-creator`, T5 `git-pr` and T6 `op-model` using the corrected import convention from the beginning of each remaining skill, keeping all six on the existing branch with one eventual PR. The user also stated, verbatim: "Do not launch a broad architecture audit during this migration." and "Do not create new branches or separate PRs per skill." and "Do not add unnecessary test frameworks or review rounds." and "Do not change unrelated Python utilities." Recorded as the continuation basis for T4–T6; no separate record is opened.

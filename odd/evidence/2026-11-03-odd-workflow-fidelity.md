# Evidence file — ODD workflow fidelity and instruction organization

> **Record:** [odd/tasks/2026-11-03-odd-workflow-fidelity.md](../tasks/2026-11-03-odd-workflow-fidelity.md) — the sole authoritative intent, task and status record for this feature.
> **Owner:** Cipher 🔓 (Lead Orchestrator); extraction authored by Scribe ✍️ (Docs & Problems Manager), instance `scribe-record-author-1`
> **Created:** 2026-11-03

## What this file is for

Hold the attestational evidence behind this feature record's `## Log`: obligation accounting, reviewer verdicts and identities, original/candidate identities, literal commands with observed results, and the preservation mapping for the compaction recorded at `L57`. Record entries point here as `E#`.

## What this file is not

Disposable working evidence. It is not a feature record, task tracker, status register, intent authority, approval, adoption proof or delivery evidence. A verdict, hash or observed result recorded here establishes only what its own entry states; no entry here certifies feature completion, runtime adoption, mirror synchronization or vendor fidelity.

## Three evidence classes

- **Decisive** — requests, corrections, approvals and their labels, decisions, obligations, acceptance limits and commits: permanent, always in the record, never here.
- **Attestational** — who verified what, with which input identity, literal command and observed result: lives here while the feature is active so the record stays readable.
- **Reproducible** — content a reader can regenerate or re-read from Git, a committed artifact, or a gitignored `output/` artifact: referenced by pointer, never copied.

Retention and close-time reconciliation are owned by `.opencode/skills/odd-workflow/SKILL.md` → `### Evidence retention`; the boundary against a durable surface citing a specific evidence file is owned by `knowledge/agent-workflow.md` → `### Feature document`; this file records one instance under that rule.

## Extraction limits

- Source: the record's `## Log` at its pre-compaction revision, whose size and identity are recorded in `E2`. Only text the available read surface returned completely is quoted below; the compacted revision's identity is the coordinator's to measure.
- Record entry `L37` (2,499 characters, the record's maximum line) exceeded tool readability. It was not read, moved, summarized, reformatted or copied, and its content appears nowhere in this file. The per-source obligation inventory therefore exists only in the record, byte-identical and flagged.

## E1 — obligation accounting

- Per-source obligation inventory (`ROOT`, `WORKFLOW`, `SHARED`, `SKILL`/`CHECKLIST` retention and translation statements): retained in the record at `L37`, unread, byte-identical, flagged. Not extracted here; a read path that returns the complete line is required first.
- Readable accounting statements extracted from the record: `L41` (round-2 verdict: valid original owner obligations retained or translated except the explicitly selected no-mirror/blanket-pause exclusions and the conflicting "only" wording; role/delegation, safety, evidence, coordination, architecture, reporting, bootstrap, records, semantic-close and release rules retained; backend bindings translated to project; mirror procedure moved to workflow); `L42` (Vault: complete skill/checklist accounting, Template C, justified version advance, no registry update required); `L43` (all 14 owner/skill cross-references resolve); `L54` (51 Log entries mapped with no gap or duplicate).
- `L54` inventory counts, verbatim: 8 requests/corrections, 12 approvals, 20 evidence/returns, 11 decision/plan entries = 51 mapped.
- `L54` observed limitations retained, not expanded: T1–T5 stay `open` because `done` requires a commit; BLOCKED remains prose-only until a separately authorized validator change.

## E2 — original and candidate identities

Record revision this extraction was taken from (`L48`): 46,848 bytes over 169 lines, SHA-256 `5eab5bf17d7bd47be91a65b95d151c81412609abae885dc2b0035d336633ae23`, with the maximum line `L37` at 2,499 characters. The compacted revision that replaced it is unmeasured here; measuring it is the coordinator's check.

Original source SHA256 identities (`L36`), measured with `Get-FileHash -Algorithm SHA256` over the five named paths — these identify source inputs, not reviewed candidate output:

| Source | SHA-256 |
|---|---|
| `AGENTS.md` | `B9F3712BF036E096ED1E0127858C91887D1B03882F5CDD97AA9A10EBCA79F954` |
| `knowledge/agent-workflow.md` | `9433001FABB46CF0078766018F5930886BAA36B37395D89D5C677C39A32EF7C0` |
| `knowledge/agents.md` | `961F6122174EE77E770C604274198F95C4B88D3E40D6E72324B94D23E95642A0` |
| `.opencode/skills/odd-workflow/SKILL.md` | `52C6C46324E6752E7257BA81A8459BF40C893572339BCD971B0E67D114526B14` |
| `.opencode/skills/odd-workflow/references/_checklist.md` | `8161A60B8DD2A2B05F96BCABF2C75FD5076B1B41E077267E718995D29449056E` |

T6 candidate identities after the `L40` corrections (`L41`): root `5BA9CE842E8A689A4430790BE208F514A1907459172BC9EE0C1969D6C2B4DA6F`, workflow `4829362E74C0FF2C7EB1AC7BD9197F4FA0C5FBE69BF9376DE43CAD077CB8BBE4`, shared `6064D49DDC7496DE4AFE7F7CA0D7444A8B40C8F8FFAD3A2927693C029C58D451`.

T7 consumer checkpoint identities (`L42`): skill `79983B7E863EEBA9AA1A3CBE221112327184A182613715A5009C2DE1B548CE94` at version 2.0.0; checklist `BA085F8240ED276C5EB695899D33107B9FC3AEBA5906C2A6DC31725ED52C5793`.

Preserved original copies used by reviewers (`L39`): `C:/Users/dexm7/AppData/Local/Temp/opencode/odd-fidelity-originals/{root/AGENTS.md,knowledge/agent-workflow.md,knowledge/agents.md}` and `.../skill/`, re-measured equal to the original identities above. Temporary copies supplement, never replace, repository/Git preservation evidence.

Per-file first-slice forecast (`L38`, planning estimate): root +42/−18; workflow +128/−22; shared +6/−1; skill +8/−3; checklist +6/−2; record +30/−6 = 372 authored additions plus deletions.

Git-measured first work unit (`L43`, `L45`): `git diff --numstat` root +18/−10, workflow +87/−6, shared +3/−1, skill +8/−3, checklist +7/−2, new record +158 = 303; Git's own count at commit = 284 insertions plus 22 deletions = 306 authored changed lines. Both below the ~400 strategy trigger.

## E3 — reviewer verdicts and identities

| Entry | Instance / session | Verdict and limits |
|---|---|---|
| `L9` | Sentinel 🛡️ (Quality Guardian), `sentinel-1`, `ses_e6021e38fffeLAZ1zv38N2MqGM` | Corrected the write-only ODD claim, rejected zero-runtime-effect inference from a profile pointer, confirmed duplication with unique obligations, identified the root approval-wording conflict. UNCERTAIN about overall prior-analysis reliability, not feature acceptance |
| `L14` | Augur 🔮 (Research Analyst), `augur-1`, `ses_e60127588ffegW4P0gVfQ8bf7B` | Pinned upstream `main` at `7d3528877d987765e4e5c504ed6049c3da7c4f4c` via HTTPS; documentary node/edge coverage only; no writes/installations; resources released |
| `L18` | Marshal 🎖️ (HR Director), `marshal-1`, `ses_e600ffdb1ffeF55ekryIt6c1C3` | Inventory only; 17 profiles, 16 specialist runtimes; no full semantic audit of specialist bodies or scenario execution claimed; all reads ceased; resources released |
| `L21` | Augur 🔮 (Research Analyst), `augur-mirror-1`, `ses_e600bfd8bffeCgtK2AI7e9lU1l` | Inspected `https://unpkg.com/@memories.sh/cli@0.7.9/dist/index.js` and `dist/chunk-WQX5ZEZ2.js`, registry metadata and current tool docs; no memory calls or mutations; resources released |
| `L27` | Sentinel 🛡️ (Quality Guardian), `sentinel-plan-1`, `ses_e60052072ffeBY9XGHvT1z7gsl` | FAIL, one finding (S9 did not incorporate the authorized probe); planning scope only |
| `L28` | same reviewer, fresh full read through `L27` | PASS, zero open findings, planning-proposal scope only; no implementation or whole-feature certification |
| `L39` | Scribe ✍️ (Docs & Problems Manager), `scribe-author-1` | Authored the three owner paths; parent checkpoint returned; resources released |
| `L40` | Sentinel 🛡️ (Quality Guardian), `sentinel-owner-1` | FAIL: F1 root heading rename violated SP-1; F2 root version classification unresolved |
| `L41` | Sentinel 🛡️ (Quality Guardian) | Round 2 PASS, zero open findings; owner-only gate accepted; T7/combined/runtime acceptance pending; no third round authorized or needed |
| `L42` | Vault 🔐 (Catalog Steward) | PASS for the changed-skill source contract, Template C, zero open findings, complete accounting, version advance justified, no registry update required |
| `L42` | Sentinel 🛡️ (Quality Guardian) | Combined PASS for reviewed source-contract scope, zero open findings; S4 not applicable to this slice, S6 deferred outside it; no vendor-prose completeness or runtime-adoption certification |
| `L54` | Scribe ✍️ (Docs & Problems Manager), `scribe-record-design-1` | Read-only design proposal; no write, commit or acceptance claimed |
| `L55` | Augur 🔮 (Research Analyst), `augur-transfer-1` | Transfer-interface findings only; no installation, code change or backend mutation |

## E4 — literal commands and observed results

- `L8` bounded search: repository Markdown searched for `flowchart TD` and distinctive supplied labels — no operational copy of the diagram found. Search evidence only, not proof of execution behavior.
- `L23` disposable probe (authorized at `L22`): `memories_add_memory` with type `note`, marker/tag `ODDMIRRORPROBE20261103CIPHER7D352887`, project `github.com-personal/JPerezC92/ai-core`, synthetic locator, revision 1 and beginning/middle/end sentinels → returned ID `sGVqoro6HIvt` and confirmed project. `memories_list_memories(limit=2,tags=[marker],types=[note])` and `memories_search_memories(query=marker,limit=2,types=[note])` → that single project-scoped ID with complete visibly expected payload (Markdown, quotes, backslashes, Unicode, table, code fences). `memories_edit_memory(id=sGVqoro6HIvt,content=revision-2-payload,metadata=revision-2)` → revision 2 with the appended synthetic Log line; independent search returned the same ID, revision 2, added line and all sentinels. `memories_forget_memory(id=sGVqoro6HIvt)` → cleanup confirmed; final marker search returned "No memories found matching your query." Storage warnings suggested vacuum; none was run. Tool-visible comparison only — not a mechanical byte/hash comparison, and not a maximum-size, concurrent-writer or restart-persistence test.
- `L28` feature validator: `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks/2026-11-03-odd-workflow-fidelity.md` → exit 0, `ok odd/tasks/2026-11-03-odd-workflow-fidelity.md`.
- `L35` release-owner preflight (Herald 📯 (Release Manager)): worktree inventory at main HEAD `0a38b37de8c22e97595ae145ef9da109a022d94f` found only this untracked record; created branch `docs/odd/align-workflow-fidelity` at that unchanged HEAD; no staging, commit or other change; operations/resources released.
- `L43` coordinator outcome checks, all executed: feature validator → `ok`; `uv run --frozen python3 .opencode/skills/op-skill-creator/scripts/check_markdown_text.py --policy knowledge/unicode-policy.json` over `AGENTS.md`, `knowledge/agent-workflow.md`, `knowledge/agents.md`, ODD skill/checklist and the record → exit 0, no diagnostics; supplied-diagram versus canonical-diagram extraction comparison → exact text match; targeted cross-reference check → all 14 owner/skill dependencies resolve (one initial apparent miss was a coordinator em-dash transcription artifact, confirmed by direct heading read); `git diff --numstat` → 303 authored additions plus deletions. Textual walkthroughs recorded in the record were not runtime execution.
- `L45` first work-unit commit: `4fe3bb316b32929101ecb5ee97fc262aa39ac789` on `docs/odd/align-workflow-fidelity`, exactly the six authorized paths, worktree clean afterwards; no push/PR/merge/tag/archive.
- `L48` record measurement before mirroring: 46,848 bytes, 169 lines, one line above the tool ceiling (`L37`, 2,499 characters). Read and grep surfaces truncated that line; the same truncation was independently reported by the reviewer at `L41`/`L42`. No mirror memory was created.

## E5 — preservation mapping

Source entries are the record's `## Log` at its pre-compaction revision; `L57` is the entry this compaction added.

| Log entry | Content class | Disposition | Content now at |
|---|---|---|---|
| `L1`–`L6` | decisive (verbatim requests/corrections, including the `L5` mermaid diagram) | kept verbatim | record |
| `L7` | decisive (approval label and scope limits) | kept | record |
| `L8` | attestational (inspection and bounded search) | compacted | record `L8`; search detail E4 |
| `L9` | attestational (reviewer verdict) | compacted | record `L9`; identity E3 |
| `L10`–`L13` | decisive (classification, footprint, checkpoints, approval) | kept | record |
| `L14` | mixed (planning return plus acceptance limits) | compacted, limits kept | record `L14`; identity/method E3 |
| `L15` | decisive (user direction, verbatim) | kept verbatim | record |
| `L16`, `L17` | decisive (approval labels and limits) | kept | record |
| `L18` | attestational (inventory return) | compacted | record `L18`; identity E3 |
| `L19`, `L20` | decisive (approval labels and limits) | kept | record |
| `L21` | attestational (capability assessment) | compacted | record `L21`; identities E3 |
| `L22` | decisive (bounded probe authorization) | kept | record |
| `L23` | attestational (literal calls and observed returns) | moved | record `L23`; full detail E4 |
| `L24`–`L26` | decisive (staged plan, diagram coverage, preservation boundary) | kept | record |
| `L27`, `L28` | mixed (review findings, correction, verdicts) | compacted | record entries; identities E3; command result E4 |
| `L29`–`L35` | decisive (approval labels, exact slice scope, gates, readiness, preflight outcome) | kept | record; the preflight facts are also recorded in E4 |
| `L36` | attestational (original hashes) | moved | record `L36`; hashes E2 |
| `L37` | attestational (per-source obligation inventory), unread | retained byte-identical, flagged | record `L37` only; never copied |
| `L38` | mixed (forecast decision and per-file measurements) | compacted | record `L38`; breakdown E2 |
| `L39` | attestational (author checkpoint, preserved originals) | compacted | record `L39`; paths/identities E2 |
| `L40` | mixed (findings, correction, reviewer) | compacted | record `L40`; reviewer identity E3 |
| `L41` | mixed (round-2 verdict and accounting) | compacted | record `L41`; hashes E2; identity E3 |
| `L42` | mixed (consumer checkpoint, two verdicts) | compacted | record `L42`; hashes E2; verdicts E3 |
| `L43` | attestational (commands, outputs, walkthrough results) | compacted | record `L43`; full detail E4 |
| `L44` | decisive (mirror status pending recovery) | kept | record |
| `L45` | decisive (work-unit commit and pending items) | kept | record |
| `L46`, `L47` | decisive (approval label, scope revision, mirror plan and unverified limits) | kept | record |
| `L48` | mixed (blocking decision and measurements) | compacted, blocker kept | record `L48`; record hash E2 |
| `L49`–`L53` | decisive (verbatim corrections, approval, evidence-class model, S14 requirement) | kept verbatim | record |
| `L54` | mixed (design return, corrected defects, limits) | compacted | record `L54`; counts E1; identity E3 |
| `L55` | mixed (transfer findings plus authorization limit) | compacted | record `L55`; identity E3 |
| `L56` | decisive (second work-unit scope) | kept | record |
| `L57` | new (this compaction's own record entry) | added | record |

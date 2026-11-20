# PR workflow inputs

> Input schemas for the pull-request publication workflow: the arguments each command takes, the JSON shapes the supplied files must satisfy, and the exit codes they return. The canonical PR-body presentation format stays in `.agents/skills/git-pr/references/_pr-evidence-format.md`; the publication input contract stays in `.agents/skills/git-pr/references/_pr-publication-input.md`; this file owns only the inputs and outputs of the commands.

Read `scripts/prepare_pr_evidence.ts` and the relevant `scripts/pr_review/` production operations relative to the skill root before use; the one content command lives in `../git-pr/scripts/prepare_pr_review.ts`. Inputs are supplied UTF-8 files, not automatically authenticated observations. Missing provenance or inputs block the affected operation; never fabricate them or rebuild local prose from GitHub. Existing owners supply immutable inventory and exact paths using their authorized reads, or the `prepare-local` route derives them through read-only Git reads by that same authorized executor; this offline tool grants no collection or Git authority and makes no GitHub call.

This workflow never reads the publication input and never compares a generated artifact with an earlier one. The generated title comes from the receipt the content command produced, and the body comes from the generated body file. There is no prior-publication input, no receipt digest, no snapshot digest and no publication-state comparison in any command.

## Runtime dependency and destination provisioning

The skill declares one runtime dependency, `zod` `4.6.7`, in its `package.json`. The infrastructure adapters decode every supplied document through Zod schemas — the local inventory, the scanner snapshot and policy, and the `verify` capture pair — and hand typed records to the application operations. The field-shape schemas live only in the infrastructure adapters; the domain and application layers decide rules and comparisons over typed records. A destination provisions the package inside the skill directory, which creates `node_modules/zod`, and runs the commands from there; no development package, build step or bundle is required at run time. Tests that exercise a copied runtime provision the same single package and assert that nothing undeclared is present.

## Workflow command contracts

- `prepare-local`: requires `--pr`, `--base`, `--receipt`, `--body` and `--output`. `--pr` is a positive integer PR number and `--base` the protected base ref; `--receipt` is the generation receipt beside the generated body and `--body` the generated body. The route resolves HEAD and the base ref, computes their merge base, enumerates commit messages, reads changed paths with deletions retained and reads file bodies at the resolved head. It performs no GitHub call and fetches no persisted body.
- `prepare-snapshot`: requires `--receipt`, `--body`, `--inventory`, `--paths` and `--output`. It assembles scanner input from the receipt's generated title and the supplied body, plus the supplied immutable inventory and exact diff paths. The output is the existing scanner schema with one local title artifact, one local body artifact, the supplied commits and files. No remote prose is fetched.
- `snapshot`: lower-level compatibility path with `--input`, `--paths` and `--output`; input is already scanner-shaped. Prefer `prepare-local`, then `prepare-snapshot`, for local preparation; neither path invents collection provenance.
- `verify`: requires `--baseline`, `--current` and `--body`. Both JSON files are captures; current is the owner's authenticated persisted capture, not a head/body-only object. Every field except `body` must remain equal, including title and OPEN state, and the persisted body must equal the intended body bytes. The tool compares supplied data; it does not authenticate, fetch, publish, scan or repair.

## Content command contract

The one content command stays with the `git-pr` skill, and its arguments are unchanged by this workflow:

- `prepare_pr_review.ts --input <publication.json> --output <body.md>`: validates the JSON publication input, renders the canonical body, creates the body exclusively at `--output`, creates `<body.md>.receipt.json` beside it and prints that receipt. The same command serves both stages: an input without `review` is a creation input and an input with `review` is a review update. It takes no `--decisions`, `--baseline`, `--current`, `--previous` or digest argument, and it never compares the generated body with an earlier body, a capture or a published state.

## Generation receipt

The generation receipt is the file `<body>.receipt.json`. It carries exactly `status` (`prepared`) and `title`, and it is reserved exclusively before the body it describes. The title binds the prepared body to the publication input it came from; a receipt whose field set, status or title differs is refused with `PUBLICATION_DIVERGED`. The receipt carries no digest of the input, the body or any earlier publication, and no command compares one.

## Inventory file

The `prepare-snapshot` inventory JSON has exactly `schema` (integer `1`), `pr_number` (positive integer), `head_sha` (7–64 hex characters), `base` (nonblank string), `commit_messages` (nonempty array), and `changed_files` (nonempty array). Each commit entry has `surface: "commit-message"`, nonblank string `source`, and string `content`; each file entry has nonempty root-relative `path` without parent traversal and string `content`. `--paths` is a JSON array of unique exact diff-path strings, equal to the unique file-entry paths. Preserve deleted-file entries and owner-evidenced content; do not omit paths.

## Scanner snapshot file

The `snapshot` input is already scanner-shaped: `schema`, `pr_number`, `head_sha`, `base`, `artifacts`, `changed_files`, with exactly one `pr-title`, one `pr-body` and at least one `commit-message` artifact, each carrying `surface`, `source`, `content`.

## PR capture schema

Both capture files of `verify` — the baseline and the persisted capture — are supplied by their owner in the seven-field metadata form: `number`, `headRefOid`, `baseRefName`, `headRefName`, `state`, `title` and `body`. Supplying that form is the caller's obligation rather than a tool check: `verify` requires the two supplied captures to be objects with identical key sets and equal non-`body` values, and requires the persisted body to equal the published body bytes. Supply both captures in the same shape even when the live handoff carries more, such as `url` and `files`. The persisted capture is the owner's authenticated observation of the pull request after the publication write. The workflow skill's `verify` never redeclares that schema; it requires the persisted capture to carry exactly the intended capture's field set and values and its body to equal the published body bytes, so the persisted capture inherits the schema its owner produced.

## Decisions file

Retired. No command accepts a decisions file, and no side file carries a decision: N/A exclusions, advisory acceptance, deferrals and authorized debt are records of the publication input, validated with it. Never reconstruct one from a retired decisions file, and never treat a decision record as proof of its own authority.

## Output creation and exit codes

All output creation is exclusive; occupied paths require explicit lifecycle disposition, never hidden overwrite or competing body names. The content command creates its body exclusively and reserves its receipt exclusively beside it; `snapshot`, `prepare-snapshot` and `prepare-local` outputs are exclusive-create; existing files produce IO failure without overwrite. Allocate distinct machine-evidence snapshot paths for actual input revisions through the coordinator; these are not extra bodies. A later stage generates its body into a fresh path and keeps the earlier artifact as history. Other commands do not write files. Exit 0 emits `status: prepared` together with the `command` that produced it — the content command prints its full receipt, the workflow commands print the status and command; exit 1 reports a business rejection, including a Git-derived one and a malformed publication JSON, which returns `INPUT_INVALID`; exit 2 reports a rejected command line (an unknown, missing or malformed argument, including a non-positive `--pr`), an unreadable or unwritable path, an undecodable JSON file supplied where a document is not the input, or a Git boundary failure — git absent from `PATH`, a failing `rev-list`/`diff`/`show`/`log` read, a timeout, or non-UTF-8 Git output. None authorizes publication or acceptance.

Validation success is structural only: retain independent evidence review, N/A authority, user acceptance, debt and final combined checks. The exclusive designated writer checks live freshness immediately before its ONE final publication, then verifies saved identity/body, obtains the mandatory fresh attribution scan of the actual persisted body and completes final live reread. The writer owns every review record, tick, open-debt entry and the verdict in the publication input; Herald 📯 (Release Manager) — the sole Git and GitHub executor — performs the single publication against the writer's exact generated body file and returns the persisted capture, and the writer — not Herald 📯 (Release Manager) — verifies it. Stale head/body, failed upload or divergent readback blocks acceptance; no blind overwrite or automatic retry. Later separately authorized factual prose corrections remain serialized after observed release of evidence ownership and preserve all records, ticks and unrelated prose; every such change still needs its fresh persisted-body scan and readback.

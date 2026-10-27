# Markdown text-integrity policy

Normative machine document: `knowledge/unicode-policy.json`, schema `version` `1`. This prose defines that schema, the CLI, and editor-projection process. It is not a second character table. Exact code-point bounds, rule IDs, severities, and rationale live only in the JSON.

The JSON is project-owned. Shared skill code must not hardcode this path, invent a default policy location, or imply destination synchronization. This file adds no distribution-clearance row, CI gate, or mandatory every-task check.

## Authority

- Character classification, decoding envelope, rule table, and representable editor overrides: JSON. Discovery exclusions are not Unicode-policy data.
- CLI shape, exit codes, diagnostics, fixed IO discovery, escaped examples, acceptance intent, and residual limits: this file, matching S3/S4/S5.
- Implementation may hardcode well-formed UTF-8 decoding, the schema/validation algorithm below, and the IO contract in this file. It must not hardcode default allow-lists, C0 exceptions, warning inventories, typography code points, or Gremlins defaults.

## Preserved permission

Repository Markdown may use ordinary Unicode, including accents, non-Latin scripts, role emoji, variation selectors, and emoji joiner sequences. Those are not errors merely because they are non-ASCII. There is no ASCII-only mode, no mass normalization, and no automatic Markdown rewrite.

Typographic prose punctuation remains permitted, including verbatim quotations and en dashes in descriptive numeric ranges (also inside inline code). The six characters `U+2013`, `U+2014`, `U+2018`, `U+2019`, `U+201C`, and `U+201D` are ordinary allowed scalars. They are not runtime whitelist rules. They appear only as editor-projection overrides with Gremlins `level` `none`. Do not normalize or rewrite existing verbatim quotations to satisfy a tool.

Do not guess executable syntax from backticks and do not use a naive fence parser.

## Schema v1 (stdlib consumer)

Parse with the Python standard library only. Unknown keys, missing keys, wrong types, duplicate JSON keys, overlapping coverage, or hex/integer mismatch are policy errors (CLI exit 2). Reject booleans for integer fields (`bool` is not an integer). Reject floats. Reject extra fields on every object. `version` must be the integer `1`; other versions fail closed.

### Root object — exact keys

| Key | Type | v1 constraint |
|---|---|---|
| `version` | integer | `1` |
| `id` | string | non-empty |
| `default_classification` | string | exactly `allow` |
| `decoding` | object | see below |
| `rules` | array | objects; coverage pairwise non-overlapping |
| `editor_projection` | object | see below |

No `suppressions` key exists. Warnings do not fail validation, so no suppression interface is provided.

`default_classification` `allow` means every successfully decoded Unicode scalar that is not covered by a rule is allowed. Do not implement an all-non-ASCII whitelist.

### `decoding` — exact keys

| Key | Type | v1 constraint |
|---|---|---|
| `encoding` | string | exactly `utf-8` |
| `invalid_sequence` | object | envelope rule, not a code-point range |

`invalid_sequence` exact keys: `id` (string), `severity` (exactly `error`), `class` (string), `rationale` (string). This is the only classification that is not a scalar range. Ill-formed UTF-8 never becomes `U+FFFD` for scanning.

### `rules[]` — exact keys

Each rule has `id`, `severity`, `class`, `rationale`, and exactly one of `codepoints` or `ranges`.

- `id`: unique non-empty string across `rules` and `decoding.invalid_sequence.id`.
- `severity`: `error` or `warning` only. Not `allow`. Not `none`.
- `class`: non-empty string.
- `rationale`: non-empty string; not used for matching.

`codepoints[]` exact keys: `cp` (integer scalar), `hex` (string). `ranges[]` exact keys: `start`, `end` (inclusive integer scalars), `start_hex`, `end_hex` (strings). Require `0 <= start <= end <= 1114111`, no surrogate values `55296..57343` (`U+D800`..`U+DFFF`), and the same bounds for `cp`. Empty `codepoints`/`ranges` arrays are policy errors.

Hex form: `U+` plus uppercase hexadecimal, minimum four digits (`U+0000` .. `U+10FFFF`). The hex field must equal that canonical form of the paired integer. Adjacent ranges may touch; inclusive overlap is a policy error. Each scalar belongs to at most one rule.

### `editor_projection` — exact keys

| Key | Type | v1 instance |
|---|---|---|
| `scope` | string | `[markdown]` |
| `setting_key` | string | `gremlins.characters` |
| `overrides` | array | representable allow-overrides only |

Each override exact keys: `codepoint` (integer), `hex` (`U+` form, must match), `gremlins_key` (lowercase hexadecimal of `codepoint`, minimum four digits, no `U+` prefix), `severity` (exactly `none`), `description` (non-empty string). Codepoints and `gremlins_key` values must be unique. This object is not a clone of Gremlins extension defaults and is not mixed into `rules`.

## Decoding and scan

1. Read file bytes. Decode as UTF-8 strict. On the first ill-formed sequence, emit `decoding.invalid_sequence` (`ERR-UTF8` in this instance), then stop scanning that file. Line is `1` plus the number of `U+000A` bytes in the valid prefix. Column is `1` plus the number of successfully decoded scalars after the last `U+000A` in that prefix (or `1` if none). Also report the 1-based byte offset of the first invalid byte. Omit `U+` hex and Unicode name: there is no scalar. Do not continue with replacement characters. An unreadable path is IO (exit 2), never a crash.
2. Split lines on `U+000A` only. `U+000D` is an ordinary allowed scalar, not a line break.
3. For each scalar, if a rule covers it, emit that rule's `id` and `severity`; otherwise allow it.
4. Column is 1-based Unicode scalar index on that line. Continue after scalar errors and warnings.

TAB `U+0009`, LF `U+000A`, and CR `U+000D` are allowed because they are absent from error ranges, not because the implementation special-cases them.

## Error and warning classes (JSON owns bounds)

Errors (exit 1 when present): invalid UTF-8 envelope; NUL; unexpected C0 including DEL; C1.

Warnings (do not fail; exit 0 if no errors): Unicode `Bidi_Control` inventory including ALM `U+061C`, LRM `U+200E`, RLM `U+200F`, embeddings `U+202A`/`U+202B`, PDF `U+202C`, overrides `U+202D`/`U+202E`, and isolates `U+2066`..`U+2069`; ZWSP `U+200B`; NBSP `U+00A0`; soft hyphen `U+00AD`; replacement character `U+FFFD` as a decoded scalar.

LRM/RLM/ALM are included because they are invisible bidi marks in the same `Bidi_Control` set as formatting and isolate controls. Report them as contextual warnings. Do not infer a malicious or broken file from a highlight.

## Explicitly not flagged

Do not add rules for ZWJ `U+200D`, ZWNJ `U+200C`, or variation selectors `U+FE00`..`U+FE0F` and `U+E0100`..`U+E01EF`. Legitimate script and emoji sequences stay allowed by default. Gremlins historically highlighted ZWNJ; this policy does not.

## Editor projection

`.vscode/settings.json` may carry only the JSON `overrides` under `editor_projection.scope` / `setting_key`. Keep those six `none` entries and their `description` strings. Remove Markdown-copied Gremlins default tables. Preserve unrelated settings and all non-Markdown behavior. Do not add global `gremlins.characters` or other global editor settings.

`--check-editor PATH` compares only that representable projection: the scoped object must contain exactly those keys, each with `level` equal to override `severity` (`none`) and `description` equal to the policy description. Extra cloned defaults are drift. The checker must not require Gremlins default characters to be present.

A readable settings JSON whose representable projection differs is not a character finding. Emit one `EDITOR-DRIFT` diagnostic, severity `error`, at the settings path, with no line, column, `U+` hex, or Unicode name. List sanitized `missing`, `extra`, and `mismatched` keys (printable ASCII only). Exit 1 when this is the most severe applicable result. Missing, unreadable, symlink, or invalid JSON at that path is IO/policy failure (stderr, exit 2).

Editor highlighting cannot provide the checker's complete semantics. A live editor reload or Gremlins merge result is distinct from static validation and remains unverified until observed. Do not claim runtime editor behavior from this document.

## CLI (proposed; agrees with S3)

Entry: `.opencode/skills/op-skill-creator/scripts/check_markdown_text.py`.

```
check_markdown_text.py --policy PATH [--check-editor PATH] PATH [PATH ...]
```

- `--policy PATH` is required. Missing, unreadable, symlink, or invalid policy is stderr and exit 2, never a clean result.
- One or more explicit Markdown file or directory paths are required. No implicit repository root scan.
- `--check-editor PATH` is optional and names a settings JSON file.
- No `--fix`, no mutation, no Git, no network, no runtime dependency installation, no formatting.

### IO identity and display

Never follow symlinks (`lstat` / `abspath` + `normpath` only; not `realpath` / `Path.resolve`). Do not dedupe by followed target. Distinct abs-normpaths are distinct IO targets; identical abs-normpaths (no follow) are one target. Display and sort paths as POSIX strings (`/` separators) derived from the provided spelling plus walk parts, not from a followed target. Sort provided roots by those POSIX strings, then walk children by sorted POSIX names.

### Explicit inputs (user-supplied roots)

Inspect each explicit path without following links:

| Explicit path | Result |
|---|---|
| Missing or unreadable | stderr, exit 2; do not crash |
| Symlink file or symlink directory | stderr, exit 2; do not follow |
| Regular file whose `suffix.lower() != ".md"` | stderr, exit 2; do not scan arbitrary content |
| Regular file whose `suffix.lower() == ".md"` | scan that file |
| Real directory | enter it even when its own basename is an excluded name (user opt-in) |

A passed symlink root is retained only as an input error: no follow, no findings from the target.

### Discovery (inside an entered real directory)

- Recurse; include dot-directories; discover only regular files with `suffix.lower() == ".md"` (case-insensitive suffix, Windows-normal, deterministic).
- Discovered symlink file or directory: skip, no finding, no follow.
- Non-regular non-symlink children: skip, no finding.
- After entering the explicit directory root, do not descend into a child directory whose basename, compared case-insensitively, is one of: `.git`, `.secrets`, `secrets`, `output`, `.venv`, `venv`, `node_modules`, `__pycache__`. File names such as `output.md` are not exclusions.
- These names are fixed IO configuration in this file, not Unicode-policy JSON.

### Diagnostics and exits

Plain human text, one diagnostic per line, stable `\n`. Ordinary findings on stdout. Policy, input, and IO failures on stderr. CLI stdout and stderr are always UTF-8 with LF (`\n` only, no CRLF), including redirected pipes; set that encoding at the process IO boundary (Windows charmap/legacy code-page is a CLI encoding bug, not a Markdown/Unicode-policy ban). Positions and exit semantics are unchanged.

Stdout character finding: `{path}:{line}:{col}: {severity} {id} {U+XXXX} {name-or-minus} {excerpt}`. `line` and `col` are 1-based Unicode-scalar positions. Escape excerpts: controls and other non-printables as `U+` spellings, never raw bytes or raw controls. Sort stdout by POSIX path, line, column, rule ID.

Stdout `ERR-UTF8`: `{path}:{line}:{col}: error ERR-UTF8 byte {n}` with 1-based byte offset `n`, line/col from the valid prefix as above, no `U+` hex, no Unicode name.

Stdout `EDITOR-DRIFT`: `{settings-path}: error EDITOR-DRIFT missing={k} extra={k} mismatched={k}` with no line, column, or `U+` name. Sort as path, then line 0, column 0, ID `EDITOR-DRIFT`. Sanitize keys to printable ASCII.

| Exit | Meaning |
|---|---|
| 0 | No errors. Warnings may exist. |
| 1 | Content errors and/or `EDITOR-DRIFT`. |
| 2 | Any policy, input, or IO failure. Exit 2 takes precedence over content errors found in the same run. |

## Escaped examples

Document intentional controls with ASCII spellings only, for example `U+200B`, `U+0000`, `U+2013`. Do not paste those actual characters into policy prose, JSON rationale, or acceptance notes.

## Acceptance cases

Allowed (no finding): ASCII; accented and non-Latin prose; single and ZWJ-compound emoji; ZWNJ and variation selectors; TAB/LF/CR; en/em dashes and curly quotes in prose, quotations, and numeric ranges including inline code; escaped spellings such as `U+200B`.

Warning (non-blocking): bidi controls listed in JSON, ZWSP, NBSP, soft hyphen, decoded `U+FFFD`.

Error: NUL, unexpected C0/C1, ill-formed UTF-8, `EDITOR-DRIFT`.

Policy/input/IO failure (stderr, exit 2, wins over content errors): unknown keys, overlapping ranges, hex mismatch, missing `--policy`, missing/unreadable/symlink inputs, explicit non-`.md` file, explicit directory symlink, invalid policy JSON, invalid editor JSON. Discovered symlinks are silent skips, not failures.

## Residual limits

Mojibake that is still well-formed Unicode is not detected. Homoglyphs and TR39 confusables are out of scope. A warning is not a universal source defect.

## Original `unicode-policy.md` accounting

| Original | Disposition |
|---|---|
| Six typographic characters permitted as prose; do not rewrite verbatim quotations | Retained; encoded as default allow, not as `rules`. S4 also permits en dashes in inline-code numeric ranges. |
| Markdown-only Gremlins allowlist; six characters `none`; no global Gremlins change; non-Markdown keeps extension defaults | Retained for the six `none` overrides and the non-Markdown/global boundary. |
| Retain every other Gremlins default inside `[markdown]` | Retired by S5. Copied default tables are not a second policy. Checker owns C0/C1/bidi/ZWSP/NBSP/SHY/FFFD. |
| Live Gremlins verification of em dash/curly quote plus ZWSP error | Retired as a claimed runtime proof. Static `--check-editor` checks representable overrides only. Live reload remains unverified. |

# PR publication input

> The single structured input for a pull request. One JSON file per pull request is the only manually maintained publication content; the utility validates it and generates the Markdown description. The canonical body format stays in `.agents/skills/git-pr/references/_pr-evidence-format.md`.

The input is data, not prose. A field never carries preformatted Markdown, and the rendered description is never stored back into the input.

The input is also the whole truth of the body: the utility renders it, checks the generated body against the canonical body format and creates it. It never compares the input with an earlier input, a capture or a published body, and it keeps no history, snapshot or digest of its own.

## Runtime dependency

The utility declares one runtime dependency, `zod`, which validates the input's shape before the domain validator applies the content rules. A destination that adopts this skill must provision it — the skill's runtime must resolve `zod` from its own `node_modules` — before generating a body; the dependency is not bundled with the skill source.

## Stages

| Stage         | `review` | Test item statuses       |
| ------------- | -------- | ------------------------ |
| Creation      | absent   | every item `PENDING`     |
| Review update | present  | any of the four statuses |

A creation-stage input that carries a `review` object or a non-`PENDING` item is refused.

## Root fields

| Field             | Type         | Required | Meaning                                                                    |
| ----------------- | ------------ | -------- | -------------------------------------------------------------------------- |
| `schemaVersion`   | integer      | yes      | `1`.                                                                       |
| `title`           | string       | yes      | Conventional title, `type(scope): summary`, under 70 characters, one line. |
| `summary`         | string array | yes      | One to three single-line bullets stating why the change exists.            |
| `breakingChanges` | object       | no       | `description` and `migration`, both single-line strings.                   |
| `testPlan`        | array        | yes      | At least two unique test items.                                            |
| `review`          | object       | no       | Review-stage record; absent at creation.                                   |

Unknown fields are refused at every level.

## Test item

| Field      | Type   | Required    | Meaning                                                               |
| ---------- | ------ | ----------- | --------------------------------------------------------------------- |
| `text`     | string | yes         | The exact test-plan item: the action and its expected result. Unique. |
| `status`   | enum   | yes         | `PENDING`, `PASSED`, `FAILED`, `NOT_APPLICABLE`.                      |
| `evidence` | object | conditional | Required for `PASSED` and `FAILED`; forbidden otherwise.              |
| `decision` | object | conditional | Required for `NOT_APPLICABLE`; forbidden otherwise.                   |

`evidence` carries `action` (the exact command or manual action and any consumed input), `result` (the observed verdict) and `executor` (the person or agent that performed the check).

`decision` carries `actor`, `date` (`YYYY-MM-DD`), `statement` and `evidence`. A decision records a claim to verify; it never authenticates itself.

A `PENDING` item carries neither field. A `FAILED` item keeps its failed result and never renders as a passing evidence row. A `NOT_APPLICABLE` item stays unchecked and carries no evidence row.

## Review record

| Field      | Type    | Required | Meaning                                                                                                  |
| ---------- | ------- | -------- | -------------------------------------------------------------------------------------------------------- |
| `prNumber` | integer | yes      | The pull request number.                                                                                 |
| `headSha`  | string  | yes      | The immutable head, 7 to 64 hexadecimal characters.                                                      |
| `baseRef`  | string  | yes      | The base ref, with or without the `origin/` prefix; the generated body renders it as `origin/<baseRef>`. |
| `findings` | array   | yes      | Review findings; an empty array means no findings.                                                       |
| `debt`     | array   | yes      | Independent authorized follow-ups; an empty array is valid.                                              |
| `verdict`  | object  | no       | The closing verdict, absent while review is incomplete.                                                  |

## Finding

| Field        | Type     | Required    | Meaning                                                                                     |
| ------------ | -------- | ----------- | ------------------------------------------------------------------------------------------- |
| `id`         | string   | yes         | `F1`, `F2`, and so on, in discovery order. Stable across rounds; never reused.              |
| `severity`   | enum     | yes         | `BLOCK` or `ADVISORY`; fixed at review and never changed by status.                         |
| `status`     | enum     | yes         | `OPEN`, `IN PROGRESS`, `FIXED`, `DEFERRED`, `REJECTED`.                                     |
| `evidence`   | string   | yes         | The finding, fix or refutation evidence.                                                    |
| `resolution` | string   | yes         | The owner and next action, or the verified resolution.                                      |
| `acceptance` | decision | conditional | Required for an unresolved finding included in an accepted `ADVISORY` outcome.              |
| `deferral`   | decision | conditional | Required exactly when `status` is `DEFERRED`; its `destination` names the debt destination. |

Finding identifiers are sequential: the first finding is `F1`, the second `F2`, and so on.

A deferred finding generates its own debt entry. `debt` therefore holds only follow-ups that are not already a deferred finding, and a `debt` target never repeats a finding id.

## Debt entry

| Field         | Type   | Required | Meaning                                                   |
| ------------- | ------ | -------- | --------------------------------------------------------- |
| `target`      | string | yes      | The follow-up this entry authorizes. Unique in the array. |
| `actor`       | string | yes      | Who authorized it.                                        |
| `date`        | string | yes      | `YYYY-MM-DD`.                                             |
| `statement`   | string | yes      | What was authorized.                                      |
| `evidence`    | string | yes      | The attributable source of the authorization.             |
| `destination` | string | yes      | The record that will hold the follow-up.                  |

## Verdict

| Field   | Type   | Meaning                               |
| ------- | ------ | ------------------------------------- |
| `kind`  | enum   | `PASS`, `ADVISORY` or `BLOCK`.        |
| `basis` | string | One line stating the readiness basis. |

`PASS` requires no unresolved finding, no `PENDING` or `FAILED` item and every non-applicable item to carry its decision. `ADVISORY` requires every unresolved finding to be advisory, to carry its acceptance, and the rendered basis to name the accepting actor and date. `BLOCK` records a blocked local review: it produces no publication body.

## Ownership

| Area                                                    | Writer                                                                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `title`, `summary`, `breakingChanges`, test item `text` | The content owner that drafts the pull request.                                                        |
| Test item `status`, `evidence`, `decision`              | The designated review evidence writer, from the named executor's result and the author's own decision. |
| `review` identity, findings, decisions, debt, verdict   | The designated review evidence writer.                                                                 |
| Publication and the GitHub write                        | Herald 📯 (Release Manager), which executes and never authors.                                         |

A review update never rewrites the authored fields, and it replaces the current state of the review record rather than accumulating a second copy of it.

## Examples

Creation input:

```json
{
  "schemaVersion": 1,
  "title": "fix(review): preserve evidence during publication",
  "summary": ["Preserve verified review evidence during pull request publication."],
  "testPlan": [
    { "text": "Run the focused content suite and confirm all tests pass.", "status": "PENDING" },
    { "text": "Submit invalid publication input and confirm the operation is refused.", "status": "PENDING" }
  ]
}
```

Review update input, with one passed item, one author-evidenced not-applicable item and one fixed finding:

```json
{
  "schemaVersion": 1,
  "title": "fix(review): preserve evidence during publication",
  "summary": ["Preserve verified review evidence during pull request publication."],
  "testPlan": [
    {
      "text": "Run the focused content suite and confirm all tests pass.",
      "status": "PASSED",
      "evidence": {
        "action": "pnpm --dir .agents/skills/git-pr test",
        "result": "All focused tests passed; exit 0.",
        "executor": "Forge"
      }
    },
    {
      "text": "Verify the optional platform-specific path on the affected platform.",
      "status": "NOT_APPLICABLE",
      "decision": {
        "actor": "PR author",
        "date": "2026-11-20",
        "statement": "This change does not affect the platform-specific path.",
        "evidence": "Author's scope assessment in the governing change record."
      }
    }
  ],
  "review": {
    "prNumber": 12,
    "headSha": "abc1234def5678abc1234def5678abc1234def56",
    "baseRef": "main",
    "findings": [
      {
        "id": "F1",
        "severity": "ADVISORY",
        "status": "FIXED",
        "evidence": "Focused regression test passes on the reviewed inputs.",
        "resolution": "Input validation corrected; independently verified by the reviewer."
      }
    ],
    "debt": [],
    "verdict": { "kind": "PASS", "basis": "Zero open findings; all required checks are verified." }
  }
}
```

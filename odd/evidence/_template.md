# Evidence file — feature name

> **Record:** [odd/tasks/date-feature-name.md](../tasks/date-feature-name.md) — the sole authoritative intent, task and status record for this feature.
> **Owner:** Name Emoji (Role) — author of this extraction
> **Created:** date

## What this file is for

Hold the attestational evidence behind one feature record's `## Log`: obligation accounting, reviewer verdicts and identities, original/candidate identities, literal commands with observed results, and the preservation mapping for anything moved out of the record. Each `E#` section is referenced from a record entry as `E#`.

## What this file is not

Disposable working evidence. It is not a feature record, task tracker, status register, intent authority, approval, adoption proof or delivery evidence. A verdict, hash or observed result recorded here establishes only what its own entry states; anatomy validation, a green check or a copied reviewer verdict never certifies the feature.

## Three evidence classes

- **Decisive** — requests, corrections, approvals and their labels, decisions, obligations, acceptance limits and commits: permanent, always in the record, never here.
- **Attestational** — who verified what, with which input identity, literal command and observed result: lives here while the feature is active so the record stays readable.
- **Reproducible** — content a reader can regenerate or re-read from Git, a committed artifact, or a gitignored `output/` artifact: referenced by pointer, never copied.

Retention and close-time reconciliation are owned by `.opencode/skills/odd-workflow/SKILL.md` → `### Evidence retention`; the boundary against a durable surface citing a specific evidence file is owned by `knowledge/agent-workflow.md` → `### Feature document`. This template illustrates the layout, not another rule definition.

## E1 — obligation accounting

## E2 — original and candidate identities

## E3 — reviewer verdicts and identities

## E4 — literal commands and observed results

## E5 — preservation mapping

## E6 — optional finding-triggered impact and escape trace

Illustrative fields only; omit this section when inapplicable. Procedure: `knowledge/agent-workflow.md` → `#### Finding-triggered impact reassessment and escape tracing`. Storage: skill `### Evidence retention` above. This section grants no scope or writer authority and is not a new tracker.

- Finding identity and available baseline/implementation/remediation candidate identities:
- Inspected paths, exclusions, unknown edges and coverage limitations:
- Responsible owners' inspected/assigned/changed/check evidence and input identities:
- Defect origin and evidence, separately from escape point and evidence; unknown where unsupported:
- Coordinator-validated conclusions and unresolved evidence gaps:
- Assigned writer and feature Log entry retaining decisive classifications, limitations and lessons before disposal:

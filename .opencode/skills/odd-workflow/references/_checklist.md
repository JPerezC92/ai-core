# ODD feature-document checklist

## Create

- [ ] This is authorized non-small state-changing work; read-only and small work require no feature artifact or new evidence template.
- [ ] Copy `odd/tasks/_template.md`; do not invent the format.
- [ ] Header carries Status, Owner, Created.
- [ ] `## Specs` has numbered `S#` with exact strings or acceptance checks.
- [ ] `## Tasks` has stable IDs, linked `S#`, route or owner, status (`open`, `in progress`, `done`), and commit. `pending` is only for open/in-progress tasks; done tasks cite a 7–64 character hexadecimal commit identifier.
- [ ] `## Log` starts with `L1` = the original request verbatim.

## Before the first write

- [ ] The request is authorized; read-only work stays read-only.
- [ ] Classify with the ODD test: small only when understood, risk-contained, and resumable from request plus diff; counts never decide.
- [ ] Read-only and small work create no durable feature artifact; non-small state-changing work has its authorized ODD feature document before the first mutation.
- [ ] Authorization and applicable safety/review gates are checked independently of classification.
- [ ] Feature scope is expressed through Specs/Tasks, not treated as an exclusive file partition; shared-resource overlap names its canonical owner/dependency and follows serialized-writer coordination.

## Change

- [ ] A requirement change rewrites only the affected spec.
- [ ] The affected task is reopened; unrelated tasks stay unchanged.

## Implement and verify

- [ ] Coherent tasks follow dependency order and owner gates; independent ready tasks may proceed concurrently under shared coordination rules.
- [ ] Each task defines applicable acceptance checks and collects actual evidence during implementation; its tests and documentation ship with the slice.
- [ ] Compact existing-Log evidence identifies task/spec, exact tested content/input or commit, relevant dependencies and environment/configuration, executor, literal command/invocation/arguments or manual action, expected and observed results/verdict, and applicable exit status; original execution provenance is preserved.
- [ ] No applicable executable check means actual static/manual verification or justified N/A, never an invented test or execution transcript.

## Close

- [ ] The verified outcome is reported.
- [ ] Every failed or pending check is reported.
- [ ] The next step is stated.
- [ ] A reported failure was reproduced before deciding it already works.
- [ ] Every task is `done` and has a commit reference.
- [ ] A reviewer independent of delivered-change and evidence authorship compares the actual original request/corrections, Specs, delivered content, complete obligation accounting and evidence; valid obligations are retained, translated or retired with explicit authority and rationale.
- [ ] Review checks unresolved requirements, durable evidence at its owner rather than temporary-output-only proof, shared/local ownership, source neutrality, precise invocation provenance, and current PR evidence under the canonical procedure when a PR exists.
- [ ] The existing Log records review identity, scope and result; zero findings remain open before a clean completion claim. Anatomy, a green suite, inherited marks and the author's summary are not semantic completion evidence.
- [ ] `Status` is `closed`, a `Closed:` date is present, and the Log has a `Close:` entry.
- [ ] `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` exits 0. This is mechanical anatomy only; independent semantic review and acceptance by Cipher 🔓 (Lead Orchestrator) remain required.

## Delivery

- [ ] Closing the feature document is not delivery.
- [ ] Commit, push, PR, release, and archive have explicit user authorization.
- [ ] A PR is a reviewable slice, not the accumulated branch.

## Forbidden

- [ ] No second tracker, no Engram mirror, no per-request context injection.
- [ ] No execution transcript in the Log; decisions and evidence only.

# Project symptom catalog

Project-owned symptom classes. Each class extends the shared baseline that ships
in `.aicore/core/knowledge/diagnostics/symptoms.md`; baseline classes keep the
`S-xx` form, and a class defined here carries the `LOCAL:` prefix.

An identifier is defined once. `S-xx` is never reused for a different signature,
and `LOCAL:S-xx` is scoped to this project's register. This file is created once
by the incident workflow's authorized initialization and is never overwritten.

| ID | Symptom / error signature | Required signals | Exclusions | Canonical diagnostic | Canonical fix routing |
|---|---|---|---|---|---|

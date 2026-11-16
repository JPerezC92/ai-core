# Project known-problem register

Project-owned problem patterns. The model, field meanings, lifecycle and
admission rules are owned by `.aicore/core/knowledge/diagnostics/problems.md`;
this file holds the rows. Rows for both teams (`incident` and `dev`) live in the
same table, because the model treats one register as shared knowledge.

This file is created once by the incident workflow's authorized initialization
and is never overwritten by that initialization or by synchronization.

| ID  | Date | Team | Symptom | System | Module | Problem | Discriminators | Exclusions | Evidence | Root cause | Lifecycle | Allow_exact | Status |
| --- | ---- | ---- | ------- | ------ | ------ | ------- | -------------- | ---------- | -------- | ---------- | --------- | ----------- | ------ |

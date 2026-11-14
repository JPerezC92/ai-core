<!-- core:begin -->
# Diagnostic Guidance

## Purpose

Reusable diagnostic queries and identification packs belong in destination-owned storage rather than symptom or problem register rows. The destination chooses the storage path and layout. This document does not define an automated query verifier.

## Register interaction

`.aicore/core/knowledge/diagnostics/symptoms.md` catalogs symptom classes; `.aicore/core/knowledge/diagnostics/problems.md` records evidence-backed problem patterns. A problem row retains a durable `case:` pointer and may reference a reusable identification pack with `pack:<destination-relative-pack-path>`. Register rows contain pointers, not SQL statements or result tables. A pack may contain a multi-statement or multi-result correlation. For a later `structural` ticket, follow the pack first and replay it with current-ticket keys under destination-owned execution, as directed by `.aicore/core/knowledge/agents.md`.

A symptom match does not by itself establish root cause. A new problem record requires confirmed evidence; duplicate patterns enrich or link to the existing record. Applying a fix requires user approval. Register-first identification, admission and close-out remain governed by `.aicore/core/knowledge/agents.md` and `.aicore/core/knowledge/diagnostics/problems.md`.

## Query and evidence safeguards

Follow the bounded-query and evidence rules in `.aicore/core/knowledge/agents.md`: bound each query, include filter columns in screenshot evidence, verify the target schema and environment, and replace prior-ticket parameters with current-ticket values. Use read-only diagnostics and controlled parameter binding rather than text interpolation or dynamic SQL concatenation. Do not put customer-specific query output in reusable queries; handle raw output under destination policy and protect credentials and sensitive data. Preserve every executed query verbatim during close-out in the ticket record or a cited validations artifact.
<!-- core:end -->

<!-- project:begin -->
## Historical context

An incident-only query-verification pilot and a broader verifier design were previously recorded here. The user directed removal of the skill in the retired query-verification debt record, which this repository retired under the seven-day retention policy on 2026-11-14; historical pilot results are not evidence of a currently available capability or destination adoption. The feature record retains the removal decision and relevant delivery history.
<!-- project:end -->

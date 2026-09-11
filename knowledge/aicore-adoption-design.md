# AICore adoption and synchronization — design

> **Status:** current
> **Scope:** Why AICore adoption splits into install and synchronization, how ownership is divided, and why the comparison needs two baselines. This document is the design rationale; the exact contract lives in `.opencode/skills/sync-aicore-adoption/references/protocol-v1.md`.

## 1. Two operations, not one

| Operation | Skill | Question it answers |
|---|---|---|
| Initial adoption | `migrate-core-to-project` | What core units is this project missing, and how are they installed? |
| Recurring synchronization | `sync-aicore-adoption` | What changed upstream, what changed locally, and what needs review? |

Installation is a one-time, additive, presence-based operation. Synchronization is a repeating, baseline-aware operation. Collapsing them into one tool would force the installer's presence-only assumptions onto updates and re-create the manual reconciliation the re-sync required.

Both read a single authoritative machine catalog (`.aicore/core-catalog-v1.yaml`) so the installed set and the comparable set never drift apart.

## 2. Independent repositories, adopted core

AICore is the upstream source of truth for core-owned content. An adopter is an independent repository that accepted a snapshot of that content, then customized parts of it. They never share a physical file.

The relationship is directional:

```text
AICore (upstream core)
        |
        |  catalog (what exists) + declaration (what the adopter intends)
        v
Adopter repository (independent files)
        |
        |  lock (what the adopter accepted)
        v
```

## 3. Ownership modes

Adopter intent is declared per unit:

| Mode | Meaning | Safe to auto-report |
|---|---|---|
| `mirror` | Must match AICore exactly | upstream-only change → `update_available` |
| `adapted` | Core unit with accepted local customization | upstream-only → `update_available`; local-only → `local_drift`; both → `review_required` |
| `replacement` | Adopter replaces the unit with its own files | always `review_required` |
| `destination_owned` | Kept locally; upstream tracked for retirement | `unmanaged` / `retirement_available` |

Ownership is adopter-specific: the same core unit may be mirrored by one project and replaced by another. That is why mode lives in the adopter declaration, never in the upstream catalog.

## 4. Why two baselines

A classic three-way comparison assumes the accepted source and the accepted destination started identical, so one baseline suffices. Adapted units violate that assumption: the adopter intentionally differs from upstream from day one.

Without an accepted **destination** baseline, the checker cannot tell whether an adapted file was changed by the adopter after acceptance or has simply always differed. Recording both `accepted_upstream_digest` and `accepted_destination_digest` per member resolves this:

- destination digest equals the accepted destination digest → no local drift;
- destination digest differs → the adopter changed it after acceptance (`local_drift` or `review_required`).

For mirrors the two accepted digests must be equal; that invariant is enforced at lock proposal and re-checked at read time.

## 5. Declaration versus lock

- `.aicore/adoption.yaml` (declaration) is **intent**: modes and destination mappings, hand-authored and reviewed.
- `.aicore/adoption.lock.yaml` (lock) is **evidence**: the accepted commit plus generated digests, produced by `propose-lock` and committed after review.

Maintainers never hand-author digests. `propose-lock` emits a candidate to stdout; the maintainer reviews and commits it. This keeps intent reviewable and evidence reproducible.

## 6. Read-only by design

The first release exposes only `check` and stdout-only `propose-lock`. There is no apply, copy, merge, or delete path. Automatic updates are deferred until ownership modes are proven across real adopters. A conflict is always reported for human review; AICore never silently reconciles local behavior.

## 7. Deterministic projection

Content is compared in a logical-member namespace using a versioned SHA-256 framing that preserves line endings, normalizes file mode, encodes symlink targets, and excludes `__pycache__/` and `*.pyc`. The `.gitignore` line-ending incident in the prior re-sync is the reason raw byte sensitivity is intentional rather than normalized away.

Units that are generated merge fragments (`sync_projection: none`) are installer-only and excluded from synchronization until a deterministic extractor exists.

## 8. Adopter configuration stays in the adopter repository

AICore ships only neutral contracts and fixtures. A real project's declaration, lock, paths, and local roles live in that project's repository under its own plan and review. This preserves the reusable-core boundary and prevents one adopter's topology from leaking into every other adopter.

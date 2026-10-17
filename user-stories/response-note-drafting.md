<!-- core:begin -->
# User story — response-note-drafting

> **Created:** 2026-10-16
> **Title:** Response note drafting
> **Status:** active
> **version:** 1.0.0
> **Epic:** incident-communication
> **Affected areas:** `.opencode/agents/quill.md`, `.opencode/agents/ledger.md`, `.opencode/skills/ticket-runbook/references/response-draft-template.md`

## Persona

- An incident analyst preparing a reader-visible response for the ticket system.

## Goal

- **G:** Deliver a reference-preserving public response draft with private evidence kept separate.
  - Done when: referenced tickets remain verified clickable links through drafting and correction; public captions remain above their images; the public handoff excludes internal evidence metadata while retaining its separate traceability; and archive handoff distinguishes actual posted text from internal metadata.

## Scenario

- A response references an incident or external problem ticket: its identifier is a hyperlink to the verified ticket-system location, whether it appears in a heading or body.
- A surgical correction changes the note: existing required links and the public/internal content boundary survive the patch and its self-audit.
- A referenced ticket lacks a verified URL: the missing input is reported rather than inventing a URL or silently using plain text.
- A response includes images: reader-visible captions appear immediately above the images, while local paths, reproduction queries, image mappings, and audit material remain separate from the public payload.
- A note has actually been posted: archive handoff preserves its posted public text and retains local evidence metadata separately, without claiming the internal metadata was published.

## Acceptance criteria

- ✅ **AC1:** Referenced ticket identifiers in the public response are hyperlinks to their verified ticket-system locations, whether they occur in a heading or body.
- ✅ **AC2:** Missing required URL evidence is reported without inventing a destination or silently replacing the required hyperlink with plain text.
- ✅ **AC3:** Drafting and patching preserve the separation between public note content and internal local paths, image mappings, reproduction queries, and audit; internal metadata is not included in the public payload.
- ✅ **AC4:** Each public image caption appears directly above its corresponding image, and separate internal mappings retain the local/remote evidence correspondence without fabricated locations.
- ✅ **AC5:** Archive handoff preserves the actual posted public text verbatim and retains internal evidence metadata separately, never describing it as published text.

## Proof

- AC1 → `.opencode/agents/quill.md` `#### Verified ticket references (hyperlinks)` · `#### Reference template` · `#### Self-audit before return (CRITICAL)` `hyperlink_preservation` · walkthrough 2026-10-16: incident and problem references rendered as `<a href>` in body prose and preserved through a surgical patch
- AC2 → `.opencode/agents/quill.md` `#### Verified ticket references (hyperlinks)` missing-URL rule ·`#### Self-audit before return (CRITICAL)` `missing_required_url` · walkthrough 2026-10-16: unverified problem URL produced a missing-input report with no draft, no plain-text fallback and no guessed host
- AC3 → `.opencode/agents/quill.md` `#### Public payload vs internal-only content` · `#### Self-audit before return (CRITICAL)` `public_payload_leak` · `.opencode/skills/ticket-runbook/references/response-draft-template.md` public/internal sections · walkthrough 2026-10-16: public slice clean in draft and patch; a pasted local `path:` line failed `public_payload_leak` while the other checks stayed green
- AC4 → `.opencode/agents/quill.md` `### Hard Rules` image discipline Label item · `#### Self-audit before return (CRITICAL)` `image_caption_label` · walkthrough 2026-10-16: both captions carry `**ImagenN — …**` directly above their `<img>`, mappings retained internally; an unlabeled caption failed only `image_caption_label`
- AC5 → `.opencode/agents/ledger.md` `#### Incremental sync per phase` (tool-returned posted text, mappings labelled archive metadata) · `#### Close-out collapse (two-stage contract)` · walkthrough 2026-10-16: the selected own note's posted text is archived verbatim with local mappings held separately, never described as published prose

## Constraints

- Drafting grants no publication authority — because posting requires the destination's authorized publishing workflow.
- Ticket URLs and evidence locations come from verified sources — because identifiers alone do not establish a valid destination or image location.
- Publisher conversion, footer removal, and post-edit HTML verification remain destination-owned — because a drafting contract cannot establish that the publishing implementation preserved the public payload.
- Durable response selection and evidence retention remain governed by the register-first incident contract — because preparing reader-visible content does not replace archive authorship or collapse checks.

<!-- core:end -->

<!-- project:begin -->
## Approval record

- 2026-10-16 — The user approved CREATE and the displayed drafting contract after catalogue/ownership and collision review, clarified that ticket references such as `#233472` must be hyperlinks rather than plain text, and subsequently authorized story persistence first. Approval is not delivery or publication authorization.

## Local evidence

- AC1–AC5 were exercised on 2026-10-16 by a clearly synthetic, non-published fixture at `/tmp/opencode/aicore-debt-fixes-20261016/drafting-case/`: a format-A draft with both incident and problem references as `<a href>`, labeled captions above remote embeds, and a clean public slice; a surgical patch that changed a value while preserving every link and label; a pasted local `path:` that failed only `public_payload_leak`; an unlabeled caption that failed only `image_caption_label`; and an unverified problem URL that produced a missing-input report with no draft. Destination publishing/HTML verification was not exercised; the delivery reference is PR #68.
- **AC4 clarification, 2026-10-16:** a rendered example showed `(ver Imagen1)` with an unlabeled caption, because remote URL embeds carry no automatic platform numbering (unlike uploaded attachments, which ticket tools label `[Image N]`) and `<img alt>` is not rendered. The caption now carries the marker itself (`**ImagenN — descripción**`), enforced by the `image_caption_label` hard check. This is a clarification of caption-to-image correspondence within AC4, not a new promise: the execution evidence for AC1–AC5 is recorded above from the 2026-10-16 synthetic fixture, and the delivery history is PR #68.

## Revision tracking

- 2026-10-16 — Approved active contract persisted. Drafting owns the public-content/handoff boundary; the register-first contract retains durable selection/retention ownership. The destination publishing implementation and its remaining footer/HTML checks are not fixed by this story revision. AC1–AC5 are established by current clauses plus a clearly synthetic 2026-10-16 drafting fixture, not by publication. Delivery history is finalized as PR #68. This file is source-authored and is not automatically cleared for distribution; no clearance, destination edit, or release action is authorized.

## Change log

- 2026-10-16 — aicore-debt-fixes-20261016 (PR #68): added verified ticket hyperlinks, the public-payload/internal-metadata split, caption labels matched to their `ImagenN` marker, and the public-leak and hyperlink-preservation audits.
<!-- project:end -->

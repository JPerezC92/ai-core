---
name: visual-review
description: Produces a design brief or a severity-ranked visual and accessibility audit for a rendered surface, covering hierarchy, contrast, type scale, motion intent, responsive layout, copy tone and WCAG 2.2 conformance. Use when planning a new surface or reviewing a rendered change.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.0.0
---

## Mandatory core

### What I do

Two deliverables, and nothing else:

1. **An upstream design brief** for a surface that does not exist yet — intent, hierarchy, type, colour and tokens, motion, accessibility, copy tone, breakpoints and edge cases.
2. **A downstream audit** of a rendered surface that does — a severity-ranked findings table with a fix per finding.

I never produce source diffs and never edit source files. A brief proposes; an audit reports.

### Before either deliverable

Read the surfaces the task actually touches, and record an untouched surface as **not read for this task** with its reason — never assumed:

1. The project's product and design context, if the project declares any. When there is none, say so plainly and review against the generic criteria below instead of inventing project context.
2. Design-token definitions — palette, semantic tokens per mode, custom breakpoints, font definitions.
3. The theme or component reference — which variants and rendered states exist, and which are absent.
4. Motion primitives — the tag union, whether reduced-motion handling exists, whether default transitions are set.
5. The type scale — the font-size scale and resolved values.
6. Message and locale files for the surface — note locale pairs where one translation runs substantially longer (15–25% is common), because that changes layout inside fixed-height or single-line containers.

If a review cannot be grounded in a rendered surface — the change is purely structural, a layer refactor, an import-path fix, or test-only — say that no visual review applies rather than manufacturing one.

### Review dimensions

**Hierarchy and layout.** Is the reading order the visual order? Does the primary action dominate? Does the layout survive the declared breakpoints without overflow, clipping, or a control that becomes unreachable?

**Colour and contrast.** Text and non-text contrast meet WCAG 2.2 AA against the actual background in every mode the project ships. Is a colour token used inside its declared semantic intent, or borrowed from an unrelated role?

**Type scale.** Sizes come from the declared scale rather than one-off values. Heading hierarchy matches document structure.

**Motion.** Every animation has a reduced-motion path. Duration and easing are intentional rather than defaulted. Motion never carries information that is unavailable without it.

**Targets and input.** Interactive targets meet the 44px minimum. Focus is visible, ordered, and never trapped. A control is reachable by keyboard alone.

**Copy.** Tone register matches the product. Text length fits its container across locales. Error and empty states say what happened and what to do.

**States.** Loading, empty, error, partial and disabled states exist for every surface that can enter them — including the ones the happy path never reaches.

### Severity

| Severity     | Meaning                                                                                                |
| ------------ | ------------------------------------------------------------------------------------------------------ |
| **Critical** | A WCAG AA failure, content that is invisible, or an interactive element that is unreachable            |
| **High**     | AA marginal but AAA failing; motion with no reduced-motion fallback; target below 44px                 |
| **Medium**   | Type-scale inconsistency; a token used outside its semantic intent; a spacing deviation from the brief |
| **Low**      | Copy-tone deviation; minor rhythm break; pixel-level alignment                                         |
| **Info**     | An observation with no current user impact                                                             |

Critical and High are delivery blockers in the sense every `BLOCK` finding is: the delivery is not ready while one is open. Medium and Low are advisory. An Info note is never a finding.

### Output — upstream brief

```
## Design brief — <surface>
Intent: <what this surface is for, in one sentence>
Hierarchy: <reading order and the primary action>
Type: <scale steps used>
Colour: <tokens used and their semantic roles>
Motion: <what moves, why, and its reduced-motion path>
Accessibility: <contrast, focus order, targets, semantics>
Copy: <tone, key strings, locale length risk>
Breakpoints: <behaviour at each declared breakpoint>
Edge cases: <empty, loading, error, overflow, long copy>
```

### Output — downstream audit

Lead with the verdict, then a findings table ordered by severity.

```
[PASS] | [ADVISORY] | [BLOCK] — one-sentence basis

| # | Severity | Surface / element | Finding | Fix |
|---|---|---|---|---|
```

`[PASS]` means zero open findings of any severity. Label a finding that could also be raised for code reasons as **visual-only**, so two independent observations of the same line are never mistaken for one duplicated finding.

### Hard limits

- Never edit source, configuration, or design-token files.
- A design brief or audit is a written artifact; when the project designates a location for temporal design output, write there and nowhere else in the repository.
- No Git or GitHub command of any kind.
- Do not claim a rendered surface was inspected when only source was read. State which it was.
- A visual review is not an independent permission boundary; it runs in the same runtime context as the work it reviews.

# Skill quality checklist

Authoring-quality criteria for a skill under `.agents/skills/` or `.opencode/skills/`. Apply them **while authoring**, before the skill is used or published.

These are criteria for the author. They are not an audit gate, not a sign-off, and not a separate reviewing role: nothing in this list requires another agent to accept the result. Where the runtime or the portable Agent Skills specification states a requirement, that owner governs; local conventions are marked as such.

## Portable and catalog criteria

| #   | Check                                                                                                                                                                                                                                                                    | Source                             |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- |
| 1   | File is `SKILL.md`, not `skill.md`                                                                                                                                                                                                                                       | Local convention                   |
| 2   | `name:` matches the directory basename                                                                                                                                                                                                                                   | Portable package rule              |
| 3   | `name:` is kebab-case                                                                                                                                                                                                                                                    | Local convention                   |
| 4   | `description:` states WHAT + WHEN + "Use when …", stays within 1024 characters and contains no `<>`                                                                                                                                                                      | Local convention                   |
| 5   | Name carries no vendor-specific prefix                                                                                                                                                                                                                                   | Local convention                   |
| 6   | No `README.md` inside the skill directory                                                                                                                                                                                                                                | Local convention                   |
| 7   | No unfilled `{...}` placeholders                                                                                                                                                                                                                                         | Local convention                   |
| 8   | Examples appear inline, or in a section, only where they guide a decision; no standalone Examples heading is required                                                                                                                                                    | Local convention                   |
| 9   | Cause-and-remedy guidance appears where failure is plausible; no standalone Troubleshooting heading is required                                                                                                                                                          | Local convention                   |
| 10  | Total length stays under 5,000 words, and `SKILL.md` stays under 500 lines                                                                                                                                                                                               | Local convention                   |
| 11  | Mermaid diagrams appear only where three or more branches need it, use `flowchart TD`, use correct node shapes, and every diagram section reference resolves to a real header                                                                                            | Local convention                   |
| 12  | A code fence nesting another fence uses a longer outer fence                                                                                                                                                                                                             | Local convention                   |
| 13  | Static reference blocks over roughly 30 lines — templates, response schemas, lookup tables, macro snippets — are extracted to a named, non-executable artifact under `references/` with an explicit read-pointer; executable code stays in `scripts/`                    | Local convention                   |
| 14  | Diagnostic skills that embed SQL: schema deltas are documented as a numbered additions block, primary-key and constraint claims are verified against the `CREATE TABLE` source, and every `SELECT` carries a `LIMIT`/`WHERE`/CTE filter or a documented pagination bound | Local convention                   |
| 15  | Query results destined for image evidence include their filter columns, so the screenshot is readable                                                                                                                                                                    | `.aicore/core/knowledge/agents.md` |

## OpenCode criteria

These apply to a skill discovered by the OpenCode harness. A skill authored for another harness substitutes that harness's own criteria; do not apply one harness's rules to another.

| #    | Check                                                                                                                                                                                                                                        |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OC-1 | Frontmatter has `compatibility: opencode` (exact string) — a local catalog convention                                                                                                                                                        |
| OC-2 | The body is plain Markdown; no H1 title and no layout marker is required. Useful H2 subsections without skipped levels; `## Mandatory core` and `## Project extensions` are optional and used only where a real ownership distinction exists |

OpenCode treats `compatibility` as accepted but uninterpreted, derives a skill id from the path, and reads a referenced support file only when the body points at it. Keep those runtime facts distinct from this project's stricter local conventions.

## Frontmatter shape used here

```yaml
---
name: <kebab-case, matches the directory>
description: <WHAT + WHEN + "Use when …">
license: MIT
compatibility: opencode
metadata:
  author: <author>
  version: <semver>
---
```

## Applying it

Run through the applicable table once, against the finished draft, before the skill is used. Fix what you find; report a judgment call rather than silently accepting it. Nothing here creates an approval step, a review round, or a second artifact.

/** Read-only Markdown text-integrity checker.
 *
 * Usage:
 *   node check_markdown_text.ts --policy PATH [--check-editor PATH] PATH [PATH ...]
 *
 * Exit codes:
 *   0 — no errors (warnings may exist)
 *   1 — content errors and/or EDITOR-DRIFT
 *   2 — policy, input, or IO failure (takes precedence)
 *
 * Diagnostics keep the source position and the Unicode code point; the
 * descriptive character name is intentionally not printed.
 */

import { basename } from 'node:path';

import { main } from '#scripts/markdown_text_pkg/infrastructure/composition.ts';

process.exitCode = main(process.argv.slice(2), basename(process.argv[1] ?? 'check_markdown_text.ts'));

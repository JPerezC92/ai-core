# Unicode punctuation policy

Repository-authored Markdown may use standard typographic punctuation when it improves readability or preserves a verbatim quotation:

- en dash — `U+2013`
- em dash — `U+2014`
- left and right single quotation marks — `U+2018`, `U+2019`
- left and right double quotation marks — `U+201C`, `U+201D`

These characters are allowed only as prose punctuation. Do not normalize or rewrite existing verbatim user quotations merely to satisfy a tool.

## Gremlins configuration

`.vscode/settings.json` applies the allowlist to `[markdown]` files only. It sets those six punctuation characters to `none` and retains every other Gremlins default, including zero-width, bidi-control, and replacement characters at their existing warning or error levels.

Code, configuration, and non-Markdown files keep the extension defaults. No global Gremlins setting is changed.

## Verification

After changing this policy or `.vscode/settings.json`, open a Markdown file containing an allowed em dash or curly quote and confirm Gremlins does not report it. Then confirm a zero-width space (`U+200B`) is still reported as an error.

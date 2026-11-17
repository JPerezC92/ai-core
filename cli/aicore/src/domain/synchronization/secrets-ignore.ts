/**
 * Domain: the destination Git ignore rule for the local secret directory.
 *
 * Enrollment never mutates the Git index. It only ensures the destination's
 * ignore file names `.secrets/` as a path, without duplicating a rule that is
 * already effective and without rewriting unrelated bytes.
 */

/** The conventional ignore rule, including its trailing newline. */
export const SECRETS_IGNORE_RULE = ".secrets/\n";

/**
 * Return the Git ignore text that carries an effective `.secrets/` rule.
 *
 * `null` means the file is absent: the result is a new file containing only
 * that rule. A present file that already ignores `.secrets` or `.secrets/` as
 * a path is returned unchanged. Commented lines do not count. Any other present
 * file keeps every existing byte, including a missing trailing newline, and
 * gains the rule on a new line.
 */
export function withSecretsIgnore(existingText: string | null): string {
	if (existingText === null) {
		return SECRETS_IGNORE_RULE;
	}
	if (ignoresSecretsPath(existingText)) {
		return existingText;
	}
	const prefix = existingText.endsWith("\n") ? existingText : `${existingText}\n`;
	return `${prefix}${SECRETS_IGNORE_RULE}`;
}

/**
 * Return whether the ignore text already names `.secrets` or `.secrets/` as a
 * path rule. A trailing comment on the same line is allowed; a commented-out
 * line is not.
 */
function ignoresSecretsPath(text: string): boolean {
	for (const line of text.split(/\r?\n/u)) {
		const trimmed = line.trim();
		if (trimmed === "" || trimmed.startsWith("#")) {
			continue;
		}
		const withoutComment = trimmed.split("#", 1)[0]?.trim() ?? "";
		if (withoutComment === ".secrets" || withoutComment === ".secrets/") {
			return true;
		}
	}
	return false;
}

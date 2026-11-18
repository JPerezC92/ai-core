/** Shared delivery-edge units for the skill's command-line entry points. */

import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

/** Escape every character outside printable ASCII as a hexadecimal escape. */
function escapeNonAscii(text: string): string {
	return text.replace(/[\u007f-\uffff]/gu, (character) => {
		const code = character.codePointAt(0) ?? 0;
		if (code <= 0xffff) return `\\u${code.toString(16).padStart(4, "0")}`;
		const adjusted = code - 0x10000;
		const high = 0xd800 + (adjusted >> 10);
		const low = 0xdc00 + (adjusted & 0x3ff);
		return `\\u${high.toString(16).padStart(4, "0")}\\u${low.toString(16).padStart(4, "0")}`;
	});
}

/** Serialize one flat payload the way the documented output is serialized. */
export function compactJson(record: Readonly<Record<string, string>>): string {
	const entries = Object.entries(record).map(
		([key, value]) => `${JSON.stringify(key)}: ${escapeNonAscii(JSON.stringify(value))}`,
	);
	return `{${entries.join(", ")}}`;
}

/** Write one line to the standard output stream. */
export function printOut(text: string): void {
	process.stdout.write(text);
}

/** Write one line to the standard error stream. */
export function printError(text: string): void {
	process.stderr.write(text);
}

/** Report whether the running process was started from the calling entry point. */
export function isDirectExecution(callerModuleUrl: string): boolean {
	const entry = process.argv[1];
	return entry !== undefined && pathToFileURL(resolve(entry)).href === callerModuleUrl;
}

/** Read local inputs and exclusively create review artifacts without overwriting. */

import { readFileSync, writeFileSync } from "node:fs";
import { TextDecoder } from "node:util";

/** Report a filesystem or decoding failure as an input/output boundary failure. */
export class InputOutputFailure extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InputOutputFailure";
  }
}

/** Decode bytes strictly, so no content is silently replaced. */
function decodeUtf8(raw: Buffer): string {
  return new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(raw);
}

/** Read UTF-8 bytes without newline translation. */
export function readText(path: string): string {
  let raw: Buffer;
  try {
    raw = readFileSync(path);
  } catch (error) {
    throw new InputOutputFailure(error instanceof Error ? error.message : String(error));
  }
  try {
    return decodeUtf8(raw);
  } catch {
    throw new InputOutputFailure("the encoded data was not valid for encoding utf-8");
  }
}

/** Create a new artifact exclusively, leaving existing files untouched. */
export function createText(path: string, content: string): void {
  try {
    writeFileSync(path, content, { encoding: "utf8", flag: "wx" });
  } catch (error) {
    throw new InputOutputFailure(error instanceof Error ? error.message : String(error));
  }
}

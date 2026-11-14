/** Read local inputs and exclusively create review artifacts without overwriting. */

import { readFileSync, writeFileSync } from 'node:fs';

/** Read UTF-8 bytes without newline translation. */
export function readText(path: string): string {
  return readFileSync(path, 'utf8');
}

/** Create a new artifact exclusively, leaving existing files untouched. */
export function createText(path: string, content: string): void {
  writeFileSync(path, content, { encoding: 'utf8', flag: 'wx' });
}

/**
 * Infrastructure: operator-local selection storage.
 *
 * The file lives inside the checkout but is gitignored, so an operator's last
 * destination never becomes repository state. Its location can be overridden so
 * tests never touch the real operator selection.
 *
 * Absence and corruption are different facts (contract C8): an absent file is a
 * genuine empty lookup result, while an unreadable or malformed file is
 * unexpected corrupt data that propagates as a boundary exception so the
 * delivery edge can report it. It is never silently coerced into "no selection",
 * which would make a corrupted file indistinguishable from a fresh checkout.
 *
 * Editor validity is a domain rule and is delegated, never re-decided here.
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

import { LOCAL_CONFIG_RELATIVE_PATH } from "#domain/constants.ts";
import type {
  SavedSelection,
  SelectionStore,
} from "#domain/ports/selection-store.ts";
import { isSupportedEditor } from "#domain/rules/selection.ts";

/** Raised when the selection file exists but cannot be used as written. */
export class CorruptSelectionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CorruptSelectionError";
  }
}

type StoredDocument = {
  readonly version: 1;
  readonly target: string;
  readonly editor: string;
};

function isMissing(error: unknown): boolean {
  return (error as { code?: string }).code === "ENOENT";
}

/** One explicit mapping step from the stored document to the domain record. */
function toSavedSelection(document: StoredDocument, path: string): SavedSelection {
  if (typeof document.target !== "string" || document.target.length === 0) {
    throw new CorruptSelectionError(
      `operator selection file has no usable destination: ${path}. ` +
        "Delete the file or re-run with --target to rewrite it.",
    );
  }
  if (typeof document.editor !== "string" || !isSupportedEditor(document.editor)) {
    throw new CorruptSelectionError(
      `operator selection file names an unsupported editor (${String(document.editor)}): ${path}. ` +
        "Delete the file or re-run with --editor to rewrite it.",
    );
  }
  return { target: document.target, editor: document.editor };
}

export class LocalJsonSelectionStore implements SelectionStore {
  readonly #path: string;

  constructor(checkoutRoot: string, overridePath?: string) {
    this.#path = overridePath ?? join(checkoutRoot, LOCAL_CONFIG_RELATIVE_PATH);
  }

  get path(): string {
    return this.#path;
  }

  async read(): Promise<SavedSelection | undefined> {
    let text: string;
    try {
      text = await readFile(this.#path, "utf8");
    } catch (error) {
      if (isMissing(error)) {
        return undefined;
      }
      throw error;
    }

    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      throw new CorruptSelectionError(
        `operator selection file is not valid JSON: ${this.#path}. ` +
          "Delete the file or re-run with --target to rewrite it.",
      );
    }

    if (typeof parsed !== "object" || parsed === null) {
      throw new CorruptSelectionError(
        `operator selection file is not a JSON object: ${this.#path}.`,
      );
    }
    const document = parsed as Record<string, unknown>;
    if (document["version"] !== 1) {
      throw new CorruptSelectionError(
        `operator selection file has an unsupported version (${String(document["version"])}): ` +
          `${this.#path}. Delete the file to start fresh.`,
      );
    }

    return toSavedSelection(document as unknown as StoredDocument, this.#path);
  }

  async write(selection: SavedSelection): Promise<void> {
    const document: StoredDocument = {
      version: 1,
      target: selection.target,
      editor: selection.editor,
    };
    await mkdir(dirname(this.#path), { recursive: true });
    await writeFile(this.#path, `${JSON.stringify(document, null, 2)}\n`, "utf8");
  }
}

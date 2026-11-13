/**
 * Domain port: reading a destination's persisted bindings document.
 *
 * Read-only by construction. A reconciliation proposal inspects what a
 * destination is bound to and never rewrites the bindings — that document is the
 * destination's own state — so the operation is given a capability that cannot
 * write it. The synchronization engine's wider `BindingsStore` satisfies this
 * port structurally.
 */

import type { BindingsDocument } from "#domain/synchronization/bindings.ts";

export interface BindingsReader {
  /** Read and validate the bindings document; `null` when absent or malformed. */
  load(path: string): Promise<BindingsDocument | null>;
}

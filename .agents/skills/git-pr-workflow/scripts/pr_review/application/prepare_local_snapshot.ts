/** Prepare scanner input using local authored title/body and supplied immutable data. */

import type { Snapshot } from "../../attribution_scan/domain/records.ts";
import { ReviewPreparationError } from "../domain/records.ts";
import { assembleSnapshot, extractDraftTitle, validateLocalInventory } from "../domain/snapshot_assembly.ts";

export class PrepareLocalSnapshot {
  /** Assemble local artifacts without fetching remote prose or collecting Git state. */
  execute(
    draft: string,
    body: string,
    inventory: unknown,
    exactPaths: unknown,
  ): Snapshot | ReviewPreparationError {
    const title = extractDraftTitle(draft);
    if (title instanceof ReviewPreparationError) return title;
    const validated = validateLocalInventory(inventory);
    if (validated instanceof ReviewPreparationError) return validated;
    if (typeof body !== "string") {
      return new ReviewPreparationError("SNAPSHOT_INVALID", "local working body must be text");
    }
    const candidate = {
      schema: validated.schema,
      pr_number: validated.pr_number,
      head_sha: validated.head_sha,
      base: validated.base,
      artifacts: [
        { surface: "pr-title", source: `PR #${validated.pr_number} title`, content: title },
        { surface: "pr-body", source: `PR #${validated.pr_number} body`, content: body },
        ...validated.commit_messages,
      ],
      changed_files: validated.changed_files,
    };
    return assembleSnapshot(candidate, exactPaths);
  }
}

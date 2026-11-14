/** Prepare a complete scanner-compatible snapshot from already collected inputs. */

import type { Snapshot } from "#scripts/attribution_scan/domain/records.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import { assembleSnapshot } from "#scripts/pr_review/domain/snapshot_assembly.ts";

export class AssembleReviewSnapshot {
  /** Reconcile supplied data without collecting Git or GitHub state. */
  execute(collected: unknown, exactPaths: unknown): Snapshot | ReviewPreparationError {
    return assembleSnapshot(collected, exactPaths);
  }
}

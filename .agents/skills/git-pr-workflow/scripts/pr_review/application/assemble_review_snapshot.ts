/** Prepare a complete scanner-compatible snapshot from already collected inputs. */

import type { Snapshot } from "../../attribution_scan/domain/records.ts";
import { ReviewPreparationError } from "../domain/records.ts";
import { assembleSnapshot } from "../domain/snapshot_assembly.ts";

export class AssembleReviewSnapshot {
  /** Reconcile supplied data without collecting Git or GitHub state. */
  execute(collected: unknown, exactPaths: unknown): Snapshot | ReviewPreparationError {
    return assembleSnapshot(collected, exactPaths);
  }
}

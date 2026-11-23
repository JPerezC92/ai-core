/**
 * Application operation: determine the effective synchronization document.
 *
 * The destination's declared opt-outs are already applied and the clearance
 * registry is already expanded for the run's editor. This operation resolves the
 * instruction root the document records, plans the enrollment a first run
 * performs, probes only the facts that decision needs, and classifies every bound
 * source into the set the run distributes, retires, or keeps for reconciliation.
 *
 * It performs no command validation and finalizes no document: the pinned
 * document is assembled from the command's own payload planner, because `pending`
 * is that planner's result and not this operation's to accept.
 */

import { ROLE_ROOT } from "#domain/synchronization/constants.ts";
import {
	type AbsentSource,
	type BindingEntry,
	type BindingsDocument,
	type EnrollmentPlan,
	enrollmentCandidates,
	withEnrolledSources,
	withheldSources,
} from "#domain/synchronization/bindings.ts";
import { drift, type SynchronizationFailure } from "#domain/synchronization/failures.ts";
import type { ClearanceEntry } from "#domain/synchronization/clearance.ts";
import type { EditorProfile } from "#domain/synchronization/editor-profile.ts";
import type { FilesystemLayout } from "#domain/synchronization/ports.ts";

import { sourceFacts, type ClearanceModes } from "./clearance-modes.ts";

/** The command intent that decides whether enrollment happens. */
export type SynchronizationIntent =
	| { readonly kind: "update" }
	| {
			readonly kind: "enroll";
			/** The explicit instruction root an enrollment may choose. */
			readonly rootOverride: string | null;
			/** Whether this run binds every cleared source (`--bind-cleared`). */
			readonly enrollUnseen: boolean;
	  };

/** What the effective document is determined from. */
export type DocumentDeterminationInput = {
	readonly document: BindingsDocument;
	readonly clearance: ClearanceModes;
	readonly editor: EditorProfile;
	readonly sourceRoot: string;
	readonly destinationRoot: string;
	readonly intent: SynchronizationIntent;
};

/** The effective document, and the classifications a command acts on. */
export type DeterminedDocument = {
	/** The document to persist: retired bindings dropped, preserved ones kept. */
	readonly document: BindingsDocument;
	/** Bindings whose source is distributed: the only ones a run writes. */
	readonly distributable: readonly BindingEntry[];
	/** Fully Core-owned sources: their destination files are deleted by the caller. */
	readonly retired: readonly AbsentSource[];
	/** Sources kept for destination reconciliation; their destinations stay. */
	readonly requiresReconciliation: readonly AbsentSource[];
	/** The root-role source the registry declares, or `null` when it declares none. */
	readonly rootSource: string | null;
	/** The resolved instruction root, or the document's recorded root. */
	readonly rootDestination: string | null;
	/** Destinations this run enrolled whose file does not exist yet. */
	readonly newRawDestinations: ReadonlySet<string>;
	/** Merge destinations this run enrolled whose file does not exist yet. */
	readonly newMergeDestinations: ReadonlySet<string>;
};

/** A determined document, or the one refusal the determination itself earns. */
export type DocumentDeterminationOutcome =
	| { readonly ok: true; readonly value: DeterminedDocument }
	| { readonly ok: false; readonly failure: SynchronizationFailure };

/** Collaborators the determination needs. */
export type PlanSynchronizationDocumentDependencies = {
	readonly layout: FilesystemLayout;
};

export class PlanSynchronizationDocument {
	readonly #dependencies: PlanSynchronizationDocumentDependencies;

	constructor(dependencies: PlanSynchronizationDocumentDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(input: DocumentDeterminationInput): Promise<DocumentDeterminationOutcome> {
		const { layout } = this.#dependencies;
		const { document: current, clearance, editor, sourceRoot, destinationRoot, intent } = input;
		const entries = clearance.entries ?? new Map<string, ClearanceEntry>();

		// The domain decides which cleared sources gain bindings and which destinations
		// are new; this operation only probes the facts it needs.
		const rootEntry = [...entries.entries()].find(([, entry]) => entry.kind === "file" && entry.role === ROLE_ROOT);
		const rootSource = rootEntry?.[0] ?? null;
		let rootDestination = current.root;
		if (rootSource !== null) {
			const existingRoot = current.bindings.find((entry) => entry.source === rootSource);
			const override = intent.kind === "enroll" ? intent.rootOverride : null;
			rootDestination =
				existingRoot?.destinations[0] ?? override ?? (await layout.detectRootFile(destinationRoot));
			if (rootDestination === null) {
				return { ok: false, failure: drift("destination instruction root not found; pass --root") };
			}
		}

		const enrollment: EnrollmentPlan =
			intent.kind === "enroll" && !intent.enrollUnseen
				? { root: current.root, candidates: [] }
				: enrollmentCandidates(current, {
						modes: clearance.modes,
						destinations: clearance.destinations,
						rootSource,
						rootDestination,
					});
		const existingDestinations = new Set<string>();
		for (const candidate of enrollment.candidates) {
			if (await layout.exists(layout.join(destinationRoot, candidate.destination))) {
				existingDestinations.add(candidate.destination);
			}
		}
		const enrolled = withEnrolledSources(current, enrollment, existingDestinations);
		// Presence is probed on the document that is classified, so a source this run
		// enrolled is asked about too: it came from a real enumeration, and the
		// classification must see that it exists.
		const facts = await sourceFacts(enrolled.document, clearance, editor, sourceRoot, layout);
		const withheld = withheldSources(enrolled.document, facts, entries);

		return {
			ok: true,
			value: {
				document: withheld.document,
				distributable: withheld.distributable,
				retired: withheld.retired,
				requiresReconciliation: withheld.requiresReconciliation,
				rootSource,
				rootDestination,
				newRawDestinations: enrolled.newRawDestinations,
				newMergeDestinations: enrolled.newMergeDestinations,
			},
		};
	}
}

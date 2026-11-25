/**
 * The bindings document: its schema rule, its declarations, and the pending rule.
 *
 * The document's *schema* is the contract's; its YAML spelling is not, so the
 * representation mapping lives at the infrastructure boundary and this module
 * sees plain parsed data. A binding carries no persisted mode in the contract —
 * the source clearance owns the distribution mode — so `declaredMode` is only
 * the in-memory hint a persisted `mode:` key or an `init` declaration supplies,
 * and it is dropped when the document is written again.
 */

import {
	BINDING_MODES,
	type BindingMode,
	MODE_MERGE,
	MODE_RAW,
	MODE_REGION,
	PROTECTED_EXCLUSION_SOURCES,
	REVISION_PATTERN,
	SCHEMA_VERSION,
} from "./constants.ts";
import type { ClearanceEntry } from "./clearance.ts";
import { declaredModeFor } from "./clearance.ts";
import { type EditorProfile, isEditorProfile } from "./editor-profile.ts";
import { type SynchronizationFailure, drift, invalid } from "./failures.ts";
import { isSafeRelativePath } from "./paths.ts";

/** One source file and the destination files that mirror it. */
export type BindingEntry = {
	readonly source: string;
	readonly destinations: readonly string[];
	/** The declaration hint; never persisted. */
	readonly declaredMode: BindingMode;
};

/** The bindings document. */
export type BindingsDocument = {
	readonly coreRevision: string | null;
	readonly root: string | null;
	/** The editor profile the destination was enrolled for; `null` when unrecorded. */
	readonly editor: EditorProfile | null;
	/**
	 * The cleared sources this destination opts out of: file paths, and directory
	 * roots ending in `/`. Empty when the destination declares none.
	 */
	readonly exclude: readonly string[];
	readonly bindings: readonly BindingEntry[];
	readonly pending: readonly string[];
};

/** The document's persisted shape, as plain data for the representation writer. */
export type BindingsRecord = {
	readonly schema: number;
	readonly core_revision: string | null;
	readonly root?: string;
	readonly editor?: string;
	/** Written only when the destination declares at least one opt-out. */
	readonly exclude?: readonly string[];
	readonly bindings: readonly {
		readonly source: string;
		readonly destinations: readonly string[];
	}[];
	readonly pending: readonly string[];
};

/**
 * Validate a parsed bindings document.
 *
 * `null` reports a malformed document: a wrong schema label, an unsafe or
 * duplicated path, an invalid revision, or a shape the schema does not allow.
 * Validation happens before any filesystem operation uses a path from it.
 */
export function parseBindingsDocument(data: unknown): BindingsDocument | null {
	if (!isRecord(data) || data["schema"] !== SCHEMA_VERSION) {
		return null;
	}
	const revision = readRevision(data["core_revision"]);
	if (revision === undefined) {
		return null;
	}
	const rawBindings = data["bindings"];
	if (!Array.isArray(rawBindings)) {
		return null;
	}
	const seen = new Set<string>();
	const bindings: BindingEntry[] = [];
	for (const rawEntry of rawBindings) {
		const entry = readBindingEntry(rawEntry, seen);
		if (entry === null) {
			return null;
		}
		bindings.push(entry);
	}
	const root = readOptionalPath(data["root"]);
	if (root === undefined) {
		return null;
	}
	const editor = readEditor(data["editor"]);
	if (editor === undefined) {
		return null;
	}
	const rawPending = data["pending"] ?? [];
	if (!Array.isArray(rawPending) || !rawPending.every((item) => typeof item === "string")) {
		return null;
	}
	const exclude = readExclusions(data["exclude"]);
	if (exclude === null) {
		return null;
	}
	return {
		coreRevision: revision,
		root,
		editor,
		exclude,
		bindings,
		pending: rawPending as string[],
	};
}

/**
 * Project a validated document onto its persisted shape.
 *
 * The editor profile is written only when the document records one, so a
 * destination enrolled before editor profiles existed keeps its own shape.
 */
export function bindingsRecord(document: BindingsDocument): BindingsRecord {
	const record: BindingsRecord = {
		schema: SCHEMA_VERSION,
		core_revision: document.coreRevision,
		...(document.root === null ? {} : { root: document.root }),
		...(document.editor === null ? {} : { editor: document.editor }),
		...(document.exclude.length === 0 ? {} : { exclude: [...document.exclude] }),
		bindings: document.bindings.map((entry) => ({
			source: entry.source,
			destinations: [...entry.destinations],
		})),
		pending: [...document.pending],
	};
	return record;
}

/** The outcome of merging `init` binding declarations into a document. */
export type DeclarationMerge = {
	readonly document: BindingsDocument;
	/** Destinations this run declared raw, for the implicit-root guard. */
	readonly newRawDestinations: ReadonlySet<string>;
	readonly failure: SynchronizationFailure | null;
};

/**
 * Merge `--bind` and `--bind-raw` declarations into a document before preflight.
 *
 * A repeatable declaration is idempotent for an identical mapping; a destination
 * already mapped to a different source is a metadata conflict.
 */
export function withInitDeclarations(
	document: BindingsDocument,
	regionSpecs: readonly string[],
	rawSpecs: readonly string[],
): DeclarationMerge {
	const destinationSources = new Map<string, string>();
	for (const entry of document.bindings) {
		for (const destination of entry.destinations) {
			destinationSources.set(destination, entry.source);
		}
	}
	const bindings = document.bindings.map((entry) => ({ ...entry }));
	const newRawDestinations = new Set<string>();
	const declarations: readonly (readonly [string, BindingMode])[] = [
		...regionSpecs.map((spec) => [spec, MODE_REGION] as const),
		...rawSpecs.map((spec) => [spec, MODE_RAW] as const),
	];

	for (const [spec, mode] of declarations) {
		const declaration = parseInitBindingSpec(spec);
		if (declaration === null) {
			return {
				document,
				newRawDestinations: new Set<string>(),
				failure: invalid(`invalid init binding: malformed or unsafe binding declaration: ${spec}`),
			};
		}
		const existingSource = destinationSources.get(declaration.destination);
		if (existingSource !== undefined) {
			if (existingSource !== declaration.source) {
				return {
					document,
					newRawDestinations: new Set<string>(),
					failure: invalid(
						`invalid init binding: destination mapping conflicts for ${declaration.destination}`,
					),
				};
			}
			continue;
		}
		const index = bindings.findIndex((entry) => entry.source === declaration.source);
		if (index === -1) {
			bindings.push({
				source: declaration.source,
				destinations: [declaration.destination],
				declaredMode: mode,
			});
		} else {
			const found = bindings[index];
			if (found === undefined) {
				continue;
			}
			bindings[index] = {
				source: found.source,
				destinations: [...found.destinations, declaration.destination],
				declaredMode: found.declaredMode,
			};
		}
		destinationSources.set(declaration.destination, declaration.source);
		if (mode === MODE_RAW) {
			newRawDestinations.add(declaration.destination);
		}
	}
	return {
		document: { ...document, bindings },
		newRawDestinations,
		failure: null,
	};
}

/** Parse one exact `SOURCE=DEST` declaration with safe paths. */
export function parseInitBindingSpec(spec: string): { readonly source: string; readonly destination: string } | null {
	const separator = spec.indexOf("=");
	if (separator === -1 || spec.indexOf("=", separator + 1) !== -1) {
		return null;
	}
	const source = spec.slice(0, separator);
	const destination = spec.slice(separator + 1);
	if (!isSafeRelativePath(source) || !isSafeRelativePath(destination)) {
		return null;
	}
	return { source, destination };
}

/** Look up a bound source's operational mode in the expanded mode map. */
export function sourceMode(source: string, modes: ReadonlyMap<string, BindingMode>): BindingMode | undefined {
	return modes.get(source);
}

/**
 * Return the raw-declaration conflict for an entry, if it has one.
 *
 * A persisted or declared `raw` whose source clearance is not `raw` fails closed:
 * the declaration is a leftover hint, and silence would let the wrong mode win.
 */
export function bindingModeConflict(
	entry: BindingEntry,
	modes: ReadonlyMap<string, BindingMode>,
): SynchronizationFailure | null {
	const mode = modes.get(entry.source);
	if (entry.declaredMode === MODE_RAW && mode !== undefined && mode !== MODE_RAW) {
		return invalid(`binding mode 'raw' conflicts with source clearance mode '${mode}' for ${entry.source}`);
	}
	return null;
}

/** Return the destinations whose source is declared raw or merge in clearance. */
export function nonRegionDestinations(
	document: BindingsDocument,
	modes: ReadonlyMap<string, BindingMode>,
): ReadonlySet<string> {
	const destinations = new Set<string>();
	for (const entry of document.bindings) {
		const mode = modes.get(entry.source);
		if (mode === MODE_RAW || mode === MODE_MERGE) {
			for (const destination of entry.destinations) {
				destinations.add(destination);
			}
		}
	}
	return destinations;
}

/** Return the pending paths that still have a region to reconcile. */
export function normalizePending(pending: readonly string[], nonRegion: ReadonlySet<string>): readonly string[] {
	return pending.filter((path) => !nonRegion.has(path));
}

/**
 * Return whether one declared opt-out covers a cleared source.
 *
 * An entry ending in `/` is a directory root and covers every source under it;
 * every other entry names one source exactly. A source is never covered by a
 * prefix that is not a directory root, so `.agents/skills/op` does not opt out
 * `.agents/skills/op-model/SKILL.md`.
 */
export function isExcludedSource(source: string, exclude: readonly string[]): boolean {
	return exclude.some((entry) => (entry.endsWith("/") ? source.startsWith(entry) : source === entry));
}

/**
 * Apply a destination's declared opt-outs to its document.
 *
 * An opted-out source keeps no binding — `apply` and `check` treat it as
 * unmanaged, so it earns no write, no drift and no uncleared-source failure —
 * and every destination that binding carried joins `pending`: the file stays on
 * disk until its owner removes it, and `check` reports the destination as not
 * current until that entry is cleared exactly as any other is.
 */
export function withOptOuts(document: BindingsDocument): BindingsDocument {
	if (document.exclude.length === 0) {
		return document;
	}
	const kept: BindingEntry[] = [];
	const dropped: string[] = [];
	for (const entry of document.bindings) {
		if (isExcludedSource(entry.source, document.exclude)) {
			dropped.push(...entry.destinations);
			continue;
		}
		kept.push(entry);
	}
	if (dropped.length === 0) {
		return document;
	}
	let pending = document.pending;
	for (const destination of dropped) {
		pending = pending.includes(destination) ? pending : [...pending, destination];
	}
	return { ...document, bindings: kept, pending };
}

/**
 * Re-establish the bindings a revoked opt-out left outstanding.
 *
 * Dropping an opted-out binding records its destination in `pending`, so a
 * `pending` path with no binding is an opt-out its owner has not reconciled.
 * Removing that entry revokes the opt-out: the source is cleared for this run,
 * no longer excluded, and its destination is still listed, so `apply` binds and
 * delivers it again and takes the path out of `pending`.
 */
export function withRestoredOptOuts(
	document: BindingsDocument,
	modes: ReadonlyMap<string, BindingMode>,
	destinations: ReadonlyMap<string, string>,
): BindingsDocument {
	const bound = new Set(document.bindings.map((entry) => entry.source));
	const outstanding = new Set(document.pending);
	const bindings = [...document.bindings];
	let restored = false;
	for (const [source, mode] of modes) {
		if (bound.has(source) || isExcludedSource(source, document.exclude)) {
			continue;
		}
		const destination = destinations.get(source);
		if (destination === undefined || !outstanding.has(destination)) {
			continue;
		}
		bindings.push({ source, destinations: [destination], declaredMode: mode });
		outstanding.delete(destination);
		restored = true;
	}
	if (!restored) {
		return document;
	}
	return {
		...document,
		bindings,
		pending: document.pending.filter((path) => outstanding.has(path)),
	};
}

/**
 * Return whether one declared opt-out overlaps a protected source.
 *
 * An entry always covers its own source and, when it is a directory root, every
 * source under it; a protected directory root additionally covers itself and
 * everything beneath it, so naming one of its files — or one of its own
 * descendant directories — is refused as surely as naming the root. This is a
 * separate predicate because `isExcludedSource` answers only the first two
 * directions, and its callers depend on that narrower meaning.
 */
function coversProtectedSource(entry: string, protectedSource: string): boolean {
	if (entry === protectedSource) {
		return true;
	}
	if (protectedSource.endsWith("/") && entry.startsWith(protectedSource)) {
		return true;
	}
	return entry.endsWith("/") && protectedSource.startsWith(entry);
}

/**
 * Return the refusal a declared opt-out earns when it names a protected source.
 *
 * The root runtime file, the harness configuration and the shared tooling
 * standard are the destination's baseline: disabling any of them would remove
 * the rule set, the configuration the enrollment merges, or the configuration
 * the distributed skills resolve against, so the request is malformed and
 * nothing is written.
 */
export function protectedExclusionFailure(document: BindingsDocument): SynchronizationFailure | null {
	const named = PROTECTED_EXCLUSION_SOURCES.filter((source) =>
		document.exclude.some((entry) => coversProtectedSource(entry, source)),
	);
	if (named.length === 0) {
		return null;
	}
	return invalid(
		`protected exclusion: ${named.join(", ")} cannot be excluded; ` + "it is a mandatory baseline resource",
	);
}

/** Why a bound source is no longer distributed. */
export type WithheldReason = "missing" | "withdrawn" | "unestablished" | "anomaly";

/** One bound source that is no longer distributed. */
export type AbsentSource = {
	readonly source: string;
	readonly destinations: readonly string[];
	readonly reason: WithheldReason;
};

/**
 * What the source tree and the clearance registry establish about the bound
 * sources, gathered as facts so the lifecycle decision stays in this domain.
 */
export type SourceFacts = {
	/** Sources the source tree still holds. */
	readonly present: ReadonlySet<string>;
	/** Sources the registry distributes to this destination's editor. */
	readonly cleared: ReadonlySet<string>;
	/** Sources the registry still covers but no longer delivers to that editor. */
	readonly withdrawn: ReadonlySet<string>;
};

/** What each bound source's lifecycle class is, and what the document becomes. */
export type WithheldSourceOutcome = {
	/** The document to persist: retired bindings dropped, preserved ones kept. */
	readonly document: BindingsDocument;
	/** Bindings whose source is distributed: the only ones a run writes. */
	readonly distributable: readonly BindingEntry[];
	/** Fully Core-owned sources: their destination files are deleted by the caller. */
	readonly retired: readonly AbsentSource[];
	/**
	 * Sources kept for destination reconciliation: their destinations stay and join
	 * `pending`. The run itself still completes its unrelated safe updates.
	 */
	readonly requiresReconciliation: readonly AbsentSource[];
};

/**
 * Classify every bound source and apply the lifecycle decision to the document.
 *
 * A cleared source is distributed. A source the registry no longer delivers is
 * classified by the ownership the registry still declares for its path, never by
 * a missing value:
 *
 * - no record covers the path: ownership cannot be established, so the
 *   destination is preserved and the reason says so;
 * - the registry withdrew the source for this editor and still declares its
 *   mode: only an exclusively Core-owned (`raw`) destination is retired, while a
 *   region-managed and a merge-managed one are preserved for reconciliation;
 * - the source still exists while the registry still delivers its path: an
 *   eligibility anomaly, preserved and reported, never deleted;
 * - the source is gone and its mode is declared: the same ownership rule
 *   applies, with the reason naming the missing source.
 *
 * A merge-managed file is never exclusively Core-owned: the merge replaces the
 * values of the keys the source declares and leaves every other key, comment and
 * formatting span as the destination owns it, so deleting it would destroy
 * destination content.
 *
 * A preserved destination keeps its binding and joins `pending`, which is what
 * withholds a verified "current" until the destination reconciles it.
 */
export function withheldSources(
	document: BindingsDocument,
	facts: SourceFacts,
	entries: ReadonlyMap<string, ClearanceEntry>,
): WithheldSourceOutcome {
	const kept: BindingEntry[] = [];
	const distributable: BindingEntry[] = [];
	const retired: AbsentSource[] = [];
	const requiresReconciliation: AbsentSource[] = [];
	let pending = document.pending;

	const preserve = (entry: BindingEntry, reason: WithheldReason): void => {
		requiresReconciliation.push({ source: entry.source, destinations: entry.destinations, reason });
		kept.push(entry);
		for (const destination of entry.destinations) {
			pending = pending.includes(destination) ? pending : [...pending, destination];
		}
	};
	const retire = (entry: BindingEntry, reason: WithheldReason): void => {
		retired.push({ source: entry.source, destinations: entry.destinations, reason });
	};

	for (const entry of document.bindings) {
		if (facts.cleared.has(entry.source) && facts.present.has(entry.source)) {
			distributable.push(entry);
			kept.push(entry);
			continue;
		}
		const ownership = declaredModeFor(entry.source, entries);
		if (ownership === null) {
			preserve(entry, "unestablished");
			continue;
		}
		if (facts.withdrawn.has(entry.source)) {
			// Only an exclusively Core-owned file may be removed. A region-managed
			// destination owns its project region and a merge-managed one owns the
			// keys the source does not declare, so both are preserved.
			if (ownership === MODE_RAW) {
				retire(entry, "withdrawn");
			} else {
				preserve(entry, "withdrawn");
			}
			continue;
		}
		if (facts.present.has(entry.source)) {
			preserve(entry, "anomaly");
			continue;
		}
		if (ownership === MODE_RAW) {
			retire(entry, "missing");
		} else {
			preserve(entry, "missing");
		}
	}

	// A destination a distributable binding claims is still in use: the obsolete
	// binding leaves the document, but the file stays for its new owner, which
	// then applies its own mode contract to it.
	const liveDestinations = new Set(distributable.flatMap((entry) => entry.destinations));
	const removals = retired
		.map((entry) => ({
			...entry,
			destinations: entry.destinations.filter((destination) => !liveDestinations.has(destination)),
		}))
		.filter((entry) => entry.destinations.length > 0);

	// A destination scheduled for physical removal has no managed file left to
	// reconcile, so its outstanding entry goes with it. A destination a live
	// binding claims is never in this set, so a shared destination, or one a
	// new binding has taken over, keeps its entry.
	const removedDestinations = new Set(removals.flatMap((entry) => entry.destinations));
	const outstanding = pending.filter((path) => !removedDestinations.has(path));

	return {
		document: { ...document, bindings: kept, pending: outstanding },
		distributable,
		retired: removals,
		requiresReconciliation,
	};
}

/** One cleared source an enrollment would bind. */
export type EnrollmentCandidate = {
	readonly source: string;
	readonly mode: BindingMode;
	readonly destination: string;
};

/** What the domain needs to plan an enrollment. */
export type EnrollmentFacts = {
	/** Every source this editor's clearance expansion distributes. */
	readonly modes: ReadonlyMap<string, BindingMode>;
	/** The destination each source lands at. */
	readonly destinations: ReadonlyMap<string, string>;
	/** The root-role source, when the registry declares one. */
	readonly rootSource: string | null;
	/** The instruction root that source must keep, or `null` when it is unknown. */
	readonly rootDestination: string | null;
};

/** The enrollment's decision before any destination is probed. */
export type EnrollmentPlan = {
	readonly root: string | null;
	readonly candidates: readonly EnrollmentCandidate[];
};

/**
 * Decide which cleared sources gain a binding, and where each lands.
 *
 * A source already bound keeps its recorded destination, an opted-out source is
 * never bound, and the root-role source keeps the instruction root the document
 * records. The caller supplies the probed facts; this decides the outcome.
 */
export function enrollmentCandidates(document: BindingsDocument, facts: EnrollmentFacts): EnrollmentPlan {
	const bound = new Set(document.bindings.map((entry) => entry.source));
	const root = facts.rootSource === null ? document.root : facts.rootDestination;
	const candidates: EnrollmentCandidate[] = [];
	for (const [source, mode] of facts.modes) {
		if (bound.has(source) || isExcludedSource(source, document.exclude)) {
			continue;
		}
		const destination =
			source === facts.rootSource && root !== null ? root : (facts.destinations.get(source) ?? source);
		candidates.push({ source, mode, destination });
	}
	return { root, candidates };
}

/** What an enrollment produced, and which destinations it creates. */
export type EnrollmentOutcome = {
	readonly document: BindingsDocument;
	readonly newRawDestinations: ReadonlySet<string>;
	readonly newMergeDestinations: ReadonlySet<string>;
};

/**
 * Apply an enrollment plan, classifying each new destination by its mode.
 *
 * `existingDestinations` is the probed fact the caller supplies: a destination
 * that is not there yet is the creation set the write-target preflight checks.
 */
export function withEnrolledSources(
	document: BindingsDocument,
	plan: EnrollmentPlan,
	existingDestinations: ReadonlySet<string>,
): EnrollmentOutcome {
	const bindings = document.bindings.map((entry) => ({ ...entry }));
	const newRawDestinations = new Set<string>();
	const newMergeDestinations = new Set<string>();
	for (const candidate of plan.candidates) {
		bindings.push({
			source: candidate.source,
			destinations: [candidate.destination],
			declaredMode: candidate.mode,
		});
		if (existingDestinations.has(candidate.destination)) {
			continue;
		}
		if (candidate.mode === MODE_RAW) {
			newRawDestinations.add(candidate.destination);
		} else if (candidate.mode === MODE_MERGE) {
			newMergeDestinations.add(candidate.destination);
		}
	}
	return { document: { ...document, bindings, root: plan.root }, newRawDestinations, newMergeDestinations };
}

/**
 * Return the destinations more than one live binding claims.
 *
 * A destination belongs to one source. A document naming it twice cannot say
 * which source owns it, and the persisted document would be rejected by
 * {@link parseBindingsDocument} on the next read, so the run is refused before
 * any filesystem mutation rather than persisting it.
 */
export function duplicatedDestinations(document: BindingsDocument): readonly string[] {
	const seen = new Set<string>();
	const duplicated: string[] = [];
	for (const entry of document.bindings) {
		for (const destination of entry.destinations) {
			if (!seen.has(destination)) {
				seen.add(destination);
				continue;
			}
			if (!duplicated.includes(destination)) {
				duplicated.push(destination);
			}
		}
	}
	return duplicated;
}

/**
 * Return the drift a bound source earns when clearance declares another
 * destination than the bindings record.
 *
 * The registry's per-editor destination is the registry's own decision, so a
 * changed one is a destination-owned migration: rewriting the bindings here
 * would move a destination's files without the operator asking, and calling the
 * destination current would hide the divergence. Only a record that declares
 * that dimension is compared — where it declares none, the destination comes
 * from the destination's own `root:` detection or an explicit declaration, and
 * the registry makes no claim to contradict.
 */
export function destinationDrift(
	document: BindingsDocument,
	entries: ReadonlyMap<string, ClearanceEntry>,
	declared: ReadonlyMap<string, string>,
): SynchronizationFailure | null {
	for (const entry of document.bindings) {
		const record = entries.get(entry.source);
		if (record === undefined || record.editors === null) {
			continue;
		}
		const destination = declared.get(entry.source);
		if (destination === undefined) {
			continue;
		}
		if (entry.destinations.length === 1 && entry.destinations[0] === destination) {
			continue;
		}
		return drift(
			`destination drift: ${entry.source} is bound to '${entry.destinations.join(", ")}' but the ` +
				`clearance registry now declares '${destination}'; a changed destination is the ` +
				"destination owner's migration, and nothing was written",
		);
	}
	return null;
}

function readBindingEntry(rawEntry: unknown, seenDestinations: Set<string>): BindingEntry | null {
	if (!isRecord(rawEntry)) {
		return null;
	}
	const source = rawEntry["source"];
	const destinations = rawEntry["destinations"];
	const rawMode = rawEntry["mode"] ?? MODE_REGION;
	if (typeof source !== "string" || !isSafeRelativePath(source)) {
		return null;
	}
	if (!Array.isArray(destinations) || destinations.length === 0) {
		return null;
	}
	const mode = BINDING_MODES.find((candidate) => candidate === rawMode);
	if (mode === undefined) {
		return null;
	}
	const resolved: string[] = [];
	for (const destination of destinations) {
		if (typeof destination !== "string" || !isSafeRelativePath(destination)) {
			return null;
		}
		if (seenDestinations.has(destination)) {
			return null;
		}
		seenDestinations.add(destination);
		resolved.push(destination);
	}
	return { source, destinations: resolved, declaredMode: mode };
}

/** Return the pinned revision, `null` for none, or `undefined` when invalid. */
function readRevision(value: unknown): string | null | undefined {
	if (value === null || value === undefined) {
		return null;
	}
	if (typeof value !== "string" || !REVISION_PATTERN.test(value)) {
		return undefined;
	}
	return value;
}

/**
 * Return the declared opt-outs, `[]` for none, or `null` when invalid.
 *
 * An entry is a cleared source path under the same canonical safe relative POSIX
 * rule every other persisted path follows; a directory root is that path with a
 * trailing `/`. Anything else is malformed bindings rather than an opt-out this
 * engine would guess at.
 */
function readExclusions(value: unknown): readonly string[] | null {
	if (value === null || value === undefined) {
		return [];
	}
	if (!Array.isArray(value)) {
		return null;
	}
	const exclude: string[] = [];
	for (const entry of value) {
		if (typeof entry !== "string") {
			return null;
		}
		const path = entry.endsWith("/") ? entry.slice(0, -1) : entry;
		if (path === "" || !isSafeRelativePath(path)) {
			return null;
		}
		exclude.push(entry);
	}
	return exclude;
}

/** Return the optional root path, `null` for none, or `undefined` when invalid. */
function readOptionalPath(value: unknown): string | null | undefined {
	if (value === null || value === undefined) {
		return null;
	}
	if (typeof value !== "string" || !isSafeRelativePath(value)) {
		return undefined;
	}
	return value;
}

/**
 * Return the enrolled editor profile, `null` for none, or `undefined` when the
 * document names an editor this build does not implement.
 *
 * An unknown editor is malformed rather than unrecorded: a document written for
 * another editor says what it was enrolled for, and reading it as unrecorded
 * would deliver that editor's payload to the wrong one.
 */
function readEditor(value: unknown): EditorProfile | null | undefined {
	if (value === null || value === undefined) {
		return null;
	}
	if (typeof value !== "string" || !isEditorProfile(value)) {
		return undefined;
	}
	return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

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
 * Return the refusal a declared opt-out earns when it names a protected source.
 *
 * The root runtime file and the harness configuration are the destination's
 * baseline: disabling either would remove the rule set or the configuration the
 * enrollment exists to deliver, so the request is malformed and nothing is
 * written.
 */
export function protectedExclusionFailure(document: BindingsDocument): SynchronizationFailure | null {
	const named = PROTECTED_EXCLUSION_SOURCES.filter((source) => isExcludedSource(source, document.exclude));
	if (named.length === 0) {
		return null;
	}
	return invalid(
		`protected exclusion: ${named.join(", ")} cannot be excluded; ` + "it is a mandatory baseline resource",
	);
}

/** Return distinct bound sources absent from clearance, in document order. */
export function unclearedSources(document: BindingsDocument, cleared: ReadonlySet<string>): readonly string[] {
	const uncleared: string[] = [];
	const seen = new Set<string>();
	for (const entry of document.bindings) {
		if (!cleared.has(entry.source) && !seen.has(entry.source)) {
			seen.add(entry.source);
			uncleared.push(entry.source);
		}
	}
	return uncleared;
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

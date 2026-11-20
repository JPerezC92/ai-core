/** Decode supplied attribution documents into typed policy and snapshot records. */

import { z } from "zod";

import { PolicyValidationError, SnapshotValidationError } from "#scripts/attribution_scan/domain/records.ts";
import type { AttributionPolicy, Snapshot } from "#scripts/attribution_scan/domain/records.ts";

/**
 * The external document shapes.
 *
 * These schemas accept the documented fields and their types only. Cross-field rules — schema
 * version, surface balance, path safety, and list membership — belong to the typed domain
 * validator and are never duplicated here.
 */
const artifactSchema = z.object({
	surface: z.string(),
	source: z.string(),
	content: z.string(),
});

const changedFileSchema = z.object({
	path: z.string(),
	content: z.string(),
});

const snapshotDocumentSchema = z.object({
	schema: z.number(),
	pr_number: z.number(),
	head_sha: z.string(),
	base: z.string(),
	artifacts: z.array(artifactSchema),
	changed_files: z.array(changedFileSchema),
});

const policyDocumentSchema = z.object({
	schema: z.number(),
	self_excluded_file: z.string(),
	markers: z.array(z.string()),
	identities: z.array(z.string()),
});

type SnapshotDocument = z.infer<typeof snapshotDocumentSchema>;
type PolicyDocument = z.infer<typeof policyDocumentSchema>;

/** Report the message a rejected snapshot document is described with. */
function snapshotIssueMessage(path: readonly PropertyKey[]): string {
	const [head, index, field] = path;
	if (head === "schema") return "snapshot schema must be 1";
	if (head === "pr_number") return "snapshot pr_number must be a positive integer";
	if (head === "head_sha") return "snapshot head_sha must contain 7 to 64 hexadecimal characters";
	if (head === "base") return "snapshot base must be a non-empty string";
	if (head === "artifacts") {
		if (index === undefined) return "snapshot artifacts must be a list";
		if (field === undefined) return "each artifact must be a JSON object";
		if (field === "surface") return "artifact surface must be pr-title, pr-body, or commit-message";
		if (field === "source") return "artifact source must be a non-empty string";
		return "artifact content must be a string";
	}
	if (head === "changed_files") {
		if (index === undefined) return "snapshot changed_files must be a list";
		if (field === undefined) return "each changed file must be a JSON object";
		if (field === "path") {
			return "changed-file path must be a non-empty root-relative path without parent traversal";
		}
		return "changed-file content must be a string";
	}
	return "snapshot must be a JSON object";
}

/** Report the message a rejected policy document is described with. */
function policyIssueMessage(path: readonly PropertyKey[]): string {
	const [head] = path;
	if (head === "schema") return "policy schema must be 1";
	if (head === "self_excluded_file") return "policy self_excluded_file must be a non-empty string";
	if (head === "markers") return "policy markers must be a non-empty string list";
	if (head === "identities") return "policy identities must be a non-empty string list";
	return "policy must be a JSON object";
}

/** Map a decoded snapshot document into the typed snapshot it carries. */
function toSnapshot(document: SnapshotDocument): Snapshot {
	return {
		schema: document.schema,
		pr_number: document.pr_number,
		head_sha: document.head_sha,
		base: document.base,
		artifacts: document.artifacts.map((artifact) => ({
			surface: artifact.surface,
			source: artifact.source,
			content: artifact.content,
		})),
		changed_files: document.changed_files.map((file) => ({ path: file.path, content: file.content })),
	};
}

/** Map a decoded policy document into the typed policy it carries. */
function toPolicy(document: PolicyDocument): AttributionPolicy {
	return {
		schema: document.schema,
		self_excluded_file: document.self_excluded_file,
		markers: [...document.markers],
		identities: [...document.identities],
	};
}

/** Decode one supplied snapshot document into typed data or a business rejection. */
export function decodeSnapshot(value: unknown): Snapshot | SnapshotValidationError {
	const parsed = snapshotDocumentSchema.safeParse(value);
	if (!parsed.success) {
		return new SnapshotValidationError(snapshotIssueMessage(parsed.error.issues[0]?.path ?? []));
	}
	return toSnapshot(parsed.data);
}

/** Decode one supplied policy document into typed data or a business rejection. */
export function decodePolicy(value: unknown): AttributionPolicy | PolicyValidationError {
	const parsed = policyDocumentSchema.safeParse(value);
	if (!parsed.success) {
		return new PolicyValidationError(policyIssueMessage(parsed.error.issues[0]?.path ?? []));
	}
	return toPolicy(parsed.data);
}

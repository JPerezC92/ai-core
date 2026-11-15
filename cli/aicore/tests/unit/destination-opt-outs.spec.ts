/**
 * Unit: the destination's declared opt-outs.
 *
 * One behavioral concern — an `exclude` entry means "this destination does not
 * want this cleared source": the source keeps no binding, its destination is
 * never deleted and is listed in `pending` instead, a revoked entry re-binds and
 * re-delivers it, and an opt-out naming the baseline is refused by name.
 */

import { describe, expect, test } from "vitest";

import {
  bindingsRecord,
  isExcludedSource,
  parseBindingsDocument,
  protectedExclusionFailure,
  withOptOuts,
  withRestoredOptOuts,
} from "#domain/synchronization/bindings.ts";
import { readDocumentText, writeBindingsDocument } from "#infrastructure/synchronization/yaml-document.ts";
import { makeBindingsDocument } from "#support/synchronization.factory.ts";

/** An optional skill directory root, as a clearance expansion names its files. */
const SKILL_ROOT = ".agents/skills/op-model/";

/** One file under that root. */
const SKILL_FILE = `${SKILL_ROOT}SKILL.md`;

/** One agent document, cleared by the `.opencode/agents/` directory root. */
const AGENT_SOURCE = ".opencode/agents/forge.md";

/** A document binding both sources to their own path. */
function makeOptOutDocument(exclude: readonly string[] = []) {
  return makeBindingsDocument({
    exclude,
    bindings: [
      { source: AGENT_SOURCE, destinations: [AGENT_SOURCE], declaredMode: "region" },
      { source: SKILL_FILE, destinations: [SKILL_FILE], declaredMode: "raw" },
    ],
  });
}

describe("declared opt-outs", () => {
  test("a file entry and a directory root drop their bindings and pend their destinations", () => {
    const dropped = withOptOuts(makeOptOutDocument([AGENT_SOURCE, SKILL_ROOT]));

    expect(dropped.bindings).toEqual([]);
    // Nothing is deleted: the destination paths are the outstanding state.
    expect(dropped.pending).toEqual([AGENT_SOURCE, SKILL_FILE]);
    // The declaration survives, so a later enrollment cannot reintroduce either.
    expect(dropped.exclude).toEqual([AGENT_SOURCE, SKILL_ROOT]);
  });

  test("only a directory root covers a prefix; a file entry names one source", () => {
    expect(isExcludedSource(SKILL_FILE, [SKILL_ROOT])).toBe(true);
    expect(isExcludedSource(SKILL_FILE, [".agents/skills/op"])).toBe(false);
    expect(isExcludedSource(AGENT_SOURCE, [AGENT_SOURCE])).toBe(true);
    expect(isExcludedSource(".opencode/agents/lumen.md", [AGENT_SOURCE])).toBe(false);
  });

  test("a document that declares no opt-out is projected unchanged", () => {
    const document = makeOptOutDocument();
    expect(withOptOuts(document)).toBe(document);
  });

  test("a revoked opt-out re-binds a cleared source whose destination is still pending", () => {
    const optedOut = withOptOuts(makeOptOutDocument([AGENT_SOURCE, SKILL_ROOT]));
    const revoked = { ...optedOut, exclude: [] };

    const restored = withRestoredOptOuts(
      revoked,
      new Map([
        [AGENT_SOURCE, "region" as const],
        [SKILL_FILE, "raw" as const],
      ]),
      new Map([
        [AGENT_SOURCE, AGENT_SOURCE],
        [SKILL_FILE, SKILL_FILE],
      ]),
    );

    expect(restored.bindings.map((entry) => entry.source)).toEqual([AGENT_SOURCE, SKILL_FILE]);
    expect(restored.pending).toEqual([]);
  });

  test("a reconciled opt-out stays absent: no pending entry, no binding", () => {
    const optedOut = withOptOuts(makeOptOutDocument([AGENT_SOURCE, SKILL_ROOT]));
    const reconciled = { ...optedOut, exclude: [], pending: [] };

    const restored = withRestoredOptOuts(
      reconciled,
      new Map([[AGENT_SOURCE, "region" as const]]),
      new Map([[AGENT_SOURCE, AGENT_SOURCE]]),
    );

    expect(restored).toBe(reconciled);
    expect(restored.bindings).toEqual([]);
  });

  test("both baseline sources are refused by name", () => {
    for (const source of ["AGENTS.md", ".opencode/opencode.jsonc"]) {
      const failure = protectedExclusionFailure(makeBindingsDocument({ exclude: [source] }));
      expect(failure?.code).toBe("invalid");
      expect(failure?.message).toContain("protected exclusion");
      expect(failure?.message).toContain(source);
    }
    expect(protectedExclusionFailure(makeBindingsDocument({ exclude: [AGENT_SOURCE] }))).toBeNull();
  });

  test("the declaration persists, and is not written when the destination declares none", () => {
    const record = bindingsRecord(makeOptOutDocument([AGENT_SOURCE, SKILL_ROOT]));
    const text = writeBindingsDocument(record);
    expect(text).toMatch(/^exclude:$/m);
    expect(text).toMatch(/^- \.agents\/skills\/op-model\/$/m);

    const read = parseBindingsDocument(readDocumentText(text));
    expect(read?.exclude).toEqual([AGENT_SOURCE, SKILL_ROOT]);

    const withoutExclusions = writeBindingsDocument(bindingsRecord(makeOptOutDocument()));
    expect(withoutExclusions).not.toMatch(/exclude/u);
  });

  test("an unsafe entry is malformed bindings, and an absent key declares no opt-outs", () => {
    for (const entry of ["../escape", "/absolute/path", ".agents\\skills\\op-model\\"]) {
      const text = [
        "schema: 1",
        "core_revision: null",
        "exclude:",
        `- ${entry}`,
        "bindings: []",
        "pending: []",
        "",
      ].join("\n");
      expect(parseBindingsDocument(readDocumentText(text)), entry).toBeNull();
    }

    // A document that declares no `exclude` key has declared no opt-outs, and an
    // unknown key elsewhere is still ignored rather than read as one.
    const absent = [
      "schema: 1",
      "core_revision: null",
      "unknown_key: ignored",
      "bindings: []",
      "pending: []",
      "",
    ].join("\n");
    expect(parseBindingsDocument(readDocumentText(absent))?.exclude).toEqual([]);
  });
});

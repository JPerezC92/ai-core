/**
 * End to end: durable destination opt-outs.
 *
 * One behavioral concern — a destination declares the cleared sources it does
 * not want in its own bindings document, and that declaration holds: a fresh
 * enrollment neither binds nor writes them, a re-enrollment never reintroduces
 * them, an opt-out declared after installation drops the binding without
 * deleting the file and reports the destination as outstanding until its owner
 * removes it, revoking it delivers the source again, and an opt-out that would
 * disable the baseline is refused by name.
 *
 * Every scenario runs the real CLI against the real engine over disposable
 * destinations only.
 */

import { mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, describe, expect, test } from "vitest";

import {
  CHECKOUT,
  REVISION,
  createFixture,
  invokeWithRevision,
  type Fixture,
} from "#support/aicore-cli.e2e-harness.ts";

/** An optional skill directory root, cleared by `distribution-clearance.json`. */
const EXCLUDED_SKILL_ROOT = ".agents/skills/op-model/";

/** One file under that root, as clearance expansion names it. */
const EXCLUDED_SKILL_FILE = `${EXCLUDED_SKILL_ROOT}SKILL.md`;

/** An optional agent document, cleared by the `.opencode/agents/` root. */
const EXCLUDED_AGENT = ".opencode/agents/forge.md";

/** An agent document the destination keeps. */
const KEPT_AGENT = ".opencode/agents/lumen.md";

/** A skill file the destination keeps. */
const KEPT_SKILL_FILE = ".agents/skills/git-commit/SKILL.md";

/** The baselines a destination may never opt out of. */
const PROTECTED_SOURCES = ["AGENTS.md", ".opencode/opencode.jsonc"];

let fixture: Fixture | undefined;

afterEach(async () => {
  await fixture?.dispose();
  fixture = undefined;
});

/** The bindings file of one destination, whose paths are relative to it. */
function bindingsPathOf(destination: string): string {
  return join(destination, ".aicore", "core.yaml");
}

/**
 * A bindings document for a destination that has never been enrolled.
 *
 * The destination's own opt-outs are part of its own state, so it declares them
 * before the first enrollment runs.
 */
function freshBindings(exclude: readonly string[]): string {
  const lines = ["schema: 1", "core_revision: null"];
  if (exclude.length > 0) {
    lines.push("exclude:");
    for (const source of exclude) {
      lines.push(`- ${source}`);
    }
  }
  lines.push("bindings: []", "pending: []", "");
  return lines.join("\n");
}

/** Seed a destination's own bindings document before it is enrolled. */
async function seedBindings(destination: string, text: string): Promise<void> {
  await mkdir(join(destination, ".aicore"), { recursive: true });
  await writeFile(bindingsPathOf(destination), text, "utf8");
}

/** The document's lines, for the edits a destination owner makes by hand. */
function linesOf(text: string): string[] {
  return text.split("\n");
}

/** Add one declared opt-out, as a destination owner writes it. */
function withExclusion(text: string, source: string): string {
  const lines = linesOf(text);
  const bindings = lines.indexOf("bindings:");
  expect(bindings).toBeGreaterThan(0);
  const existing = lines.indexOf("exclude:");
  if (existing >= 0) {
    lines.splice(existing + 1, 0, `- ${source}`);
    return lines.join("\n");
  }
  lines.splice(bindings, 0, "exclude:", `- ${source}`);
  return lines.join("\n");
}

/** Remove the whole `exclude` declaration, as a destination owner does. */
function withoutExclusionKey(text: string): string {
  const lines = linesOf(text);
  const start = lines.indexOf("exclude:");
  expect(start).toBeGreaterThan(0);
  let end = start + 1;
  while (end < lines.length && lines[end]?.startsWith("- ")) {
    end += 1;
  }
  return [...lines.slice(0, start), ...lines.slice(end)].join("\n");
}

/** The bounds of the `pending:` declaration, as a destination owner edits it. */
function pendingBounds(lines: readonly string[]): number {
  const start = lines.findIndex((line) => line.startsWith("pending:"));
  expect(start).toBeGreaterThanOrEqual(0);
  return start;
}

/** Clear the destination's own `pending` list, as its owner does. */
function clearPending(text: string): string {
  const lines = linesOf(text);
  const start = pendingBounds(lines);
  return [...lines.slice(0, start), "pending: []", ""].join("\n");
}

/** The sources the document binds, in document order. */
function boundSources(text: string): readonly string[] {
  return linesOf(text)
    .map((line) => /^- source: (.+)$/u.exec(line)?.[1])
    .filter((source): source is string => source !== undefined);
}

/** The paths the document lists under `pending:`. */
function pendingPaths(text: string): readonly string[] {
  const lines = linesOf(text);
  const start = pendingBounds(lines);
  const paths: string[] = [];
  for (const line of lines.slice(start + 1)) {
    if (!line.startsWith("- ")) {
      break;
    }
    paths.push(line.slice(2));
  }
  return paths;
}

/** Enroll one destination with the advanced engine command. */
function enroll(destination: string, created: Fixture) {
  return invokeWithRevision(
    [
      "init",
      "--source",
      CHECKOUT,
      "--destination",
      destination,
      "--bindings",
      bindingsPathOf(destination),
      "--source-revision",
      REVISION,
      "--editor",
      "opencode",
      "--bind-cleared",
    ],
    created,
  );
}

/** Run the operator's synchronization for one destination. */
function synchronize(destination: string, created: Fixture) {
  return invokeWithRevision(
    ["sync", "--target", destination, "--editor", "opencode"],
    created,
  );
}

/** Read the destination's bindings document. */
function readBindings(destination: string): Promise<string> {
  return readFile(bindingsPathOf(destination), "utf8");
}

describe("durable destination opt-outs", () => {
  test("a fresh enrollment neither installs nor binds an opted-out source, and a re-enrollment keeps it out", async () => {
    const created = await createFixture();
    fixture = created;
    const { destination } = created;
    await seedBindings(destination, freshBindings([EXCLUDED_SKILL_ROOT, EXCLUDED_AGENT]));

    const first = await enroll(destination, created);
    expect(first.status).toBe(0);
    expect(first.stdout).toMatch(/initialized/);

    // Neither the skill root nor the agent document was delivered.
    await expect(stat(join(destination, EXCLUDED_SKILL_ROOT.slice(0, -1)))).rejects.toThrow();
    await expect(stat(join(destination, EXCLUDED_AGENT))).rejects.toThrow();
    // The rest of the payload is complete, so the opt-out is not a broken run.
    expect((await stat(join(destination, KEPT_AGENT))).isFile()).toBe(true);
    expect((await stat(join(destination, KEPT_SKILL_FILE))).isFile()).toBe(true);

    // Neither source is bound, and the declaration that kept them out persists.
    const enrolled = await readBindings(destination);
    const sources = boundSources(enrolled);
    expect(sources).not.toContain(EXCLUDED_AGENT);
    expect(sources.some((source) => source.startsWith(EXCLUDED_SKILL_ROOT))).toBe(false);
    expect(sources).toContain(KEPT_AGENT);
    expect(sources).toContain(KEPT_SKILL_FILE);
    expect(enrolled).toMatch(/^exclude:$/m);
    expect(enrolled).toMatch(new RegExp(`^- ${EXCLUDED_AGENT}$`, "m"));
    expect(enrolled).toMatch(new RegExp(`^- ${EXCLUDED_SKILL_ROOT}$`, "m"));

    // A second enrollment — which enrolls any newly cleared source — changes
    // nothing about the opt-outs.
    const second = await enroll(destination, created);
    expect(second.status).toBe(0);
    await expect(stat(join(destination, EXCLUDED_SKILL_ROOT.slice(0, -1)))).rejects.toThrow();
    await expect(stat(join(destination, EXCLUDED_AGENT))).rejects.toThrow();
    const reEnrolled = await readBindings(destination);
    expect(boundSources(reEnrolled)).not.toContain(EXCLUDED_AGENT);
    expect(boundSources(reEnrolled).some((source) => source.startsWith(EXCLUDED_SKILL_ROOT))).toBe(
      false,
    );
  });

  test("an opt-out declared after installation drops the binding, deletes nothing, and reports the destination as outstanding", async () => {
    const created = await createFixture();
    fixture = created;
    const { destination } = created;

    const enrolledRun = await synchronize(destination, created);
    expect(enrolledRun.stdout).toMatch(/initialized/);
    expect((await stat(join(destination, EXCLUDED_AGENT))).isFile()).toBe(true);
    expect(boundSources(await readBindings(destination))).toContain(EXCLUDED_AGENT);

    // The destination reconciles its fresh enrollment, then opts out.
    let bindings = clearPending(await readBindings(destination));
    await writeFile(bindingsPathOf(destination), bindings, "utf8");
    const current = await synchronize(destination, created);
    expect(current.status).toBe(0);
    expect(current.stdout).toMatch(/is current/);

    await writeFile(
      bindingsPathOf(destination),
      withExclusion(bindings, EXCLUDED_AGENT),
      "utf8",
    );

    const optedOut = await synchronize(destination, created);
    // The write drops the binding; the verification reports the opt-out as an
    // outstanding reconciliation rather than a current destination.
    expect(optedOut.status).toBe(1);
    expect(optedOut.stdout).toMatch(/applied/);
    expect(optedOut.stderr).toMatch(/pending changes/);

    bindings = await readBindings(destination);
    expect(boundSources(bindings)).not.toContain(EXCLUDED_AGENT);
    // Nothing was deleted, and the file that must go is named in `pending`.
    expect((await stat(join(destination, EXCLUDED_AGENT))).isFile()).toBe(true);
    expect(pendingPaths(bindings)).toContain(EXCLUDED_AGENT);

    // The destination owner removes the file and clears that entry, exactly as
    // for any other pending path; then the destination verifies as current.
    await rm(join(destination, EXCLUDED_AGENT));
    await writeFile(bindingsPathOf(destination), clearPending(bindings), "utf8");

    const reconciled = await synchronize(destination, created);
    expect(reconciled.status).toBe(0);
    expect(reconciled.stdout).toMatch(/is current/);
    await expect(stat(join(destination, EXCLUDED_AGENT))).rejects.toThrow();
  });

  test("revoking an opt-out delivers the source again, and dropping the declaration does not restore anything by itself", async () => {
    const created = await createFixture();
    fixture = created;
    const { destination } = created;

    await synchronize(destination, created);
    let bindings = clearPending(await readBindings(destination));
    await writeFile(bindingsPathOf(destination), bindings, "utf8");
    expect((await synchronize(destination, created)).status).toBe(0);

    // Opt out of the agent document: the binding goes, the file stays.
    await writeFile(
      bindingsPathOf(destination),
      withExclusion(bindings, EXCLUDED_AGENT),
      "utf8",
    );
    expect((await synchronize(destination, created)).status).toBe(1);

    // Revoking it re-binds and re-delivers the source, and its outstanding path
    // leaves `pending`, so the destination verifies as current.
    bindings = await readBindings(destination);
    await writeFile(bindingsPathOf(destination), withoutExclusionKey(bindings), "utf8");
    const restored = await synchronize(destination, created);
    expect(restored.status).toBe(0);
    expect(restored.stdout).toMatch(/is current/);
    bindings = await readBindings(destination);
    expect(boundSources(bindings)).toContain(EXCLUDED_AGENT);
    expect(pendingPaths(bindings)).toEqual([]);
    expect((await stat(join(destination, EXCLUDED_AGENT))).isFile()).toBe(true);

    // Opt out of a whole skill root: every file under it leaves the bindings.
    await writeFile(
      bindingsPathOf(destination),
      withExclusion(bindings, EXCLUDED_SKILL_ROOT),
      "utf8",
    );
    expect((await synchronize(destination, created)).status).toBe(1);
    bindings = await readBindings(destination);
    expect(boundSources(bindings).some((source) => source.startsWith(EXCLUDED_SKILL_ROOT))).toBe(
      false,
    );
    expect(pendingPaths(bindings)).toContain(EXCLUDED_SKILL_FILE);
    expect((await stat(join(destination, EXCLUDED_SKILL_FILE))).isFile()).toBe(true);

    // Deleting the declaration restores nothing by itself: the source is simply
    // no longer excluded, and the next enrollment delivers it again.
    await writeFile(bindingsPathOf(destination), withoutExclusionKey(bindings), "utf8");
    const reEnrolled = await enroll(destination, created);
    expect(reEnrolled.status).toBe(0);
    const delivered = await synchronize(destination, created);
    expect(delivered.status).toBe(0);
    expect(delivered.stdout).toMatch(/is current/);
    bindings = await readBindings(destination);
    expect(boundSources(bindings)).toContain(EXCLUDED_SKILL_FILE);
    expect(pendingPaths(bindings)).toEqual([]);
    expect((await stat(join(destination, EXCLUDED_SKILL_FILE))).isFile()).toBe(true);
  });

  test("an opt-out naming a baseline resource is refused by name and writes nothing", async () => {
    for (const protectedSource of PROTECTED_SOURCES) {
      const created = await createFixture();
      try {
        const { destination } = created;
        await seedBindings(destination, freshBindings([protectedSource]));

        const refused = await enroll(destination, created);
        expect(refused.status).toBe(2);
        expect(refused.stderr).toContain("protected exclusion");
        expect(refused.stderr).toContain(protectedSource);

        // Nothing was written: no payload, no reconciliation report, and the
        // root runtime file still carries only the fixture's own text.
        await expect(stat(join(destination, ".opencode"))).rejects.toThrow();
        await expect(stat(join(destination, ".aicore", "reconciliation"))).rejects.toThrow();
        expect(await readFile(join(destination, "AGENTS.md"), "utf8")).toContain(
          "# Fixture project",
        );
        expect(await readBindings(destination)).toBe(freshBindings([protectedSource]));
      } finally {
        await created.dispose();
      }
    }
  });
});

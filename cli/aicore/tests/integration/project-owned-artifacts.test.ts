/**
 * Integration: project-owned artifacts are outside the distributed set.
 *
 * One behavioral concern — this repository's clearance registry clears the
 * managed ODD templates, the shared diagnostic catalogs and the incident
 * skill's local register templates, and clears nothing under the project-owned
 * roots `odd/` or `incidents/`. Synchronization therefore has no binding through
 * which it could create, overwrite or delete those records.
 */

import { readFileSync, readdirSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, test } from "vitest";

import { expandClearance, parseClearanceDocument } from "#domain/synchronization/clearance.ts";
import { CLEARANCE_FILENAME } from "#domain/synchronization/constants.ts";

const REPO_ROOT = fileURLToPath(new URL("../../../..", import.meta.url));
const PROJECT_OWNED_ROOTS = ["odd", "incidents"] as const;

function parseRegistry() {
  const text = readFileSync(join(REPO_ROOT, CLEARANCE_FILENAME), "utf8");
  const parsed = parseClearanceDocument(JSON.parse(text));
  if (!parsed.ok) throw new Error(parsed.reason);
  return parsed.entries;
}

/** Every regular file under `root`, as the clearance expansion enumerates it. */
function enumerate(root: string): string[] {
  const out: string[] = [];
  const walk = (dir: string): void => {
    for (const entry of readdirSync(join(REPO_ROOT, dir), { withFileTypes: true })) {
      const path = `${dir}/${entry.name}`;
      if (entry.isDirectory()) walk(path);
      else if (entry.isFile()) out.push(path);
    }
  };
  walk(root);
  return out.map((path) => relative(root, path).split(sep).join("/"));
}

describe("project-owned artifacts and distribution clearance", () => {
  test("no project-owned path is cleared for distribution", () => {
    const cleared = [...parseRegistry().keys()];
    expect(cleared.length).toBeGreaterThan(0);
    const leaked = cleared.filter((path) =>
      PROJECT_OWNED_ROOTS.some((root) => path === root || path.startsWith(`${root}/`)),
    );
    expect(leaked).toEqual([]);
  });

  test("managed ODD templates stay cleared as raw files", () => {
    const entries = parseRegistry();
    expect(entries.get(".aicore/core/odd/tasks/_template.md")).toMatchObject({ mode: "raw" });
    expect(entries.get(".aicore/core/odd/features/_template.md")).toMatchObject({ mode: "raw" });
  });

  test("the shared diagnostic catalogs stay managed and region-mode", () => {
    const entries = parseRegistry();
    expect(entries.get(".aicore/core/knowledge/diagnostics/")).toMatchObject({ mode: "region" });
    const root = ".aicore/core/knowledge/diagnostics/";
    const expansion = expandClearance(parseRegistry(), new Map([[root, enumerate(root)]]), "opencode");
    for (const name of ["symptoms.md", "problems.md", "diagnostic-guidance.md"]) {
      expect(expansion.modes.get(`${root}${name}`)).toBe("region");
    }
  });

  test("local register templates ship with the incident skill and bind no project register", () => {
    const skillRoot = ".agents/skills/incident-workflow/";
    const expansion = expandClearance(
      parseRegistry(),
      new Map([[skillRoot, enumerate(skillRoot)]]),
      "opencode",
    );
    for (const name of ["local-symptoms-template.md", "local-problems-template.md"]) {
      expect(expansion.modes.get(`${skillRoot}references/${name}`)).toBe("raw");
    }
    const bound = [...expansion.destinations.keys()].filter((path) => path.startsWith("incidents/"));
    expect(bound).toEqual([]);
  });
});

import { describe, expect, test } from "vitest";

import { isMerged, mergeTopLevel } from "#domain/synchronization/merge.ts";

const source = `{
  "mcp": {
    "servers": {
      "system-one": { "type": "local", "command": ["node", "mcp-servers/system-one/src/mcp/stdio.ts"] },
      "qmd": { "type": "local", "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "ai-core", "mcp"] }
    }
  }
}`;

describe("omit_mcp_servers", () => {
  test("a first merge does not write omitted servers and retargets qmd", () => {
    const omit = new Set(["system-one"]);
    const merged = mergeTopLevel(source, "{}", "widget", omit);
    expect(merged).not.toBeNull();
    expect(merged).not.toMatch(/system-one/);
    expect(merged).toMatch(/widget/);
    expect(isMerged(source, merged ?? "", "widget", omit)).toBe(true);
  });

  test("check stays current when the destination never received the omitted server", () => {
    const omit = new Set(["system-one"]);
    const destination = `{
      "mcp": {
        "servers": {
          "qmd": { "type": "local", "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "widget", "mcp"] }
        }
      }
    }`;
    expect(isMerged(source, destination, "widget", omit)).toBe(true);
    expect(isMerged(source, destination, "widget")).toBe(false);
  });
});

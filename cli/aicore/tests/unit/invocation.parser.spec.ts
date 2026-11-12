/**
 * Unit: the invocation parser.
 *
 * One behavioral concern — turning an argument vector into a typed invocation
 * (contract T2: the approved parser/loader unit target).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";

import { parseInvocation } from "#domain/rules/invocation.ts";
import { REVISION } from "#support/aicore-cli.factory.ts";

describe("parseInvocation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("no arguments asks for help", () => {
    const parsed = parseInvocation([]);
    expect(parsed).toEqual({ ok: true, value: { kind: "help" } });
  });

  test("sync with no options yields an unset sync invocation", () => {
    const parsed = parseInvocation(["sync"]);
    expect(parsed.ok).toBeTruthy();
    expect(parsed.ok && parsed.value.kind).toBe("sync");
    if (parsed.ok && parsed.value.kind === "sync") {
      expect(parsed.value.target).toBe(undefined);
      expect(parsed.value.editor).toBe(undefined);
      expect(parsed.value.revision).toBe(undefined);
    }
  });

  test("sync collects target, editor and revision", () => {
    const parsed = parseInvocation([
      "sync",
      "--target",
      "../project",
      "--editor",
      "opencode",
      "--source-revision",
      REVISION,
    ]);
    expect(parsed).toEqual({
      ok: true,
      value: {
        kind: "sync",
        target: "../project",
        editor: "opencode",
        revision: REVISION,
        help: false,
      },
    });
  });

  test("sync rejects an unknown option", () => {
    const parsed = parseInvocation(["sync", "--dest", "x"]);
    expect(!parsed.ok).toBeTruthy();
    expect(parsed.ok ? "" : parsed.failure.message).toMatch(/unrecognized option "--dest"/);
  });

  test("sync rejects an option without a value", () => {
    const parsed = parseInvocation(["sync", "--target"]);
    expect(!parsed.ok).toBeTruthy();
    expect(parsed.ok ? "" : parsed.failure.message).toMatch(/requires a value/);
  });

  test("sync rejects a repeated option", () => {
    const parsed = parseInvocation(["sync", "--target", "a", "--target", "b"]);
    expect(!parsed.ok).toBeTruthy();
    expect(parsed.ok ? "" : parsed.failure.message).toMatch(/more than once/);
  });

  test("advanced commands forward arguments untouched", () => {
    const parsed = parseInvocation(["check", "--source", ".", "--destination", "../d"]);
    expect(parsed).toEqual({
      ok: true,
      value: {
        kind: "advanced",
        command: "check",
        passthrough: ["--source", ".", "--destination", "../d"],
        help: false,
      },
    });
  });

  test("an unknown command names the known commands", () => {
    const parsed = parseInvocation(["deploy"]);
    expect(!parsed.ok).toBeTruthy();
    const message = parsed.ok ? "" : parsed.failure.message;
    expect(message).toMatch(/unknown command "deploy"/);
    expect(message).toMatch(/check, apply, init/);
  });
});

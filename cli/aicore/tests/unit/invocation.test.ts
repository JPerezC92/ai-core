/**
 * Unit: the invocation parser.
 *
 * One behavioral concern — turning an argument vector into a typed invocation,
 * plus the two closed-value resolutions that share the parser's module.
 */

import assert from "node:assert/strict";
import { describe, test } from "node:test";

import {
  parseInvocation,
  resolveEditor,
  resolveRevision,
} from "#domain/rules/invocation.ts";
import { OTHER_REVISION, REVISION } from "#support/aicore-cli.factory.ts";

describe("parseInvocation", () => {
  test("no arguments asks for help", () => {
    const parsed = parseInvocation([]);
    assert.deepEqual(parsed, { ok: true, value: { kind: "help" } });
  });

  test("sync with no options yields an unset sync invocation", () => {
    const parsed = parseInvocation(["sync"]);
    assert.ok(parsed.ok);
    assert.equal(parsed.ok && parsed.value.kind, "sync");
    if (parsed.ok && parsed.value.kind === "sync") {
      assert.equal(parsed.value.target, undefined);
      assert.equal(parsed.value.editor, undefined);
      assert.equal(parsed.value.revision, undefined);
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
    assert.deepEqual(parsed, {
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
    assert.ok(!parsed.ok);
    assert.match(parsed.ok ? "" : parsed.failure.message, /unrecognized option "--dest"/);
  });

  test("sync rejects an option without a value", () => {
    const parsed = parseInvocation(["sync", "--target"]);
    assert.ok(!parsed.ok);
    assert.match(parsed.ok ? "" : parsed.failure.message, /requires a value/);
  });

  test("sync rejects a repeated option", () => {
    const parsed = parseInvocation(["sync", "--target", "a", "--target", "b"]);
    assert.ok(!parsed.ok);
    assert.match(parsed.ok ? "" : parsed.failure.message, /more than once/);
  });

  test("advanced commands forward arguments untouched", () => {
    const parsed = parseInvocation(["check", "--source", ".", "--destination", "../d"]);
    assert.deepEqual(parsed, {
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
    assert.ok(!parsed.ok);
    const message = parsed.ok ? "" : parsed.failure.message;
    assert.match(message, /unknown command "deploy"/);
    assert.match(message, /check, apply, init/);
  });
});

describe("resolveEditor", () => {
  test("accepts the implemented editor", () => {
    assert.deepEqual(resolveEditor("opencode"), { ok: true, value: "opencode" });
  });

  test("refuses the planned editor by name without substituting another", () => {
    const resolved = resolveEditor("cursor");
    assert.ok(!resolved.ok);
    const message = resolved.ok ? "" : resolved.failure.message;
    assert.match(message, /not implemented/);
    assert.match(message, /Nothing was written/);
  });

  test("refuses an unknown editor", () => {
    const resolved = resolveEditor("vim");
    assert.ok(!resolved.ok);
    assert.match(resolved.ok ? "" : resolved.failure.message, /unknown editor "vim"/);
  });
});

describe("resolveRevision", () => {
  test("uses the explicit value when supplied", () => {
    assert.deepEqual(resolveRevision(REVISION, undefined), { ok: true, value: REVISION });
  });

  test("falls back to the operator setting", () => {
    assert.deepEqual(resolveRevision(undefined, REVISION), { ok: true, value: REVISION });
  });

  test("the explicit value wins over the setting", () => {
    assert.deepEqual(resolveRevision(REVISION, OTHER_REVISION), { ok: true, value: REVISION });
  });

  test("reports the missing revision without running Git", () => {
    const resolved = resolveRevision(undefined, undefined);
    assert.ok(!resolved.ok);
    const message = resolved.ok ? "" : resolved.failure.message;
    assert.match(message, /never runs Git/);
    assert.match(message, /Herald/);
  });

  test("rejects a revision that is not 40 lowercase hex characters", () => {
    for (const candidate of ["abc", "A".repeat(40), "g".repeat(40), `${REVISION}0`]) {
      assert.ok(!resolveRevision(candidate, undefined).ok, candidate);
    }
  });
});

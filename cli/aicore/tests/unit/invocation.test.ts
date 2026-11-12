/**
 * Unit: the invocation parser.
 *
 * One behavioral concern — turning an argument vector into a typed invocation
 * (contract T2: the approved parser/loader unit target).
 */

import assert from "node:assert/strict";
import { describe, test } from "node:test";

import { parseInvocation } from "#domain/rules/invocation.ts";
import { REVISION } from "#support/aicore-cli.factory.ts";

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

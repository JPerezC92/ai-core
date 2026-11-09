// Behaviour tests of the portable System 1 advisory edge's connection binding: the connection the
// plugin builds for itself when composition supplies no evaluator, its once-per-setup laziness and
// its teardown, and the binding that connection states — its interpreter, the host executable it
// must not restart and the inherited resolution environment it carries. No case spawns a process,
// reaches the network or contacts a model endpoint: the default path runs through a recording
// factory double, and the binding is read through the adapter's own pure builder.

import { afterEach, describe, expect, test, vi } from 'vitest';

import { getDefaultEnvironment } from '@modelcontextprotocol/client/stdio';

import { ADVISORY_BLOCK_START } from './index.ts';
import {
  createAdviserHarness,
  createDefaultConnectionExpectation,
  createMessageIdentity,
  createOutgoingContext,
} from './test/helpers/plugin.factory.ts';

// The inherited value the PATH case installs, so the carried entry is judged against a value the
// test states rather than against the machine that happens to run it (T18).
const STATED_PATH = '/odd-adviser-test/bin:/usr/bin';

// The observed defect this group covers: the host supplies the plugin context alone, so a
// composition that reports `caller_unavailable` whenever no evaluator arrives never reaches the
// MCP at all. These cases pin the replacement arrangement — the plugin builds its own connection,
// once per setup, only when it is first used, and closes it at teardown — without spawning.
describe('plugin default connection', () => {
  test('creates one default connection on the first evaluation and evaluates through it', async () => {
    const harness = await createAdviserHarness({ evaluator: null, timeoutMs: null });

    // Setup alone composes nothing: a plugin that is loaded but unused reaches no process.
    expect(harness.connections).toHaveLength(0);

    const first = createOutgoingContext(createMessageIdentity(1));
    const second = createOutgoingContext(createMessageIdentity(2));
    await harness.build(first);
    await harness.build(second);

    // Two messages, one connection: the connection is owned by the setup, not by a message.
    expect(harness.connections).toHaveLength(1);
    const connection = harness.connections[0];
    expect(connection?.evaluations).toHaveLength(2);
    // The documented default bound stands when composition states none.
    expect(connection?.evaluations[0]?.options.timeoutMs).toBe(15_000);
    // Each build received an advisory block, and the evaluation reported the delivered outcome
    // rather than the unavailable status the defect produced.
    expect(first.system).toHaveLength(1);
    expect(first.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
    expect(
      harness.events
        .filter((event) => event.stage === 'evaluate_finished')
        .map((event) => event.code),
    ).toStrictEqual(['evaluated', 'evaluated']);
  });

  test('uses the supplied evaluator and creates no default connection', async () => {
    const harness = await createAdviserHarness();

    await harness.build(createOutgoingContext(createMessageIdentity()));

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(harness.connections).toHaveLength(0);
  });

  test('closes the default connection at teardown', async () => {
    const harness = await createAdviserHarness({ evaluator: null, timeoutMs: null });
    await harness.build(createOutgoingContext(createMessageIdentity()));

    const connection = harness.connections[0];
    expect(connection?.closes).toBe(0);

    await harness.cleanup();

    expect(connection?.closes).toBe(1);
  });

  test('tears down a plugin that was never evaluated without creating a connection', async () => {
    const harness = await createAdviserHarness({ evaluator: null, timeoutMs: null });

    await harness.cleanup();

    expect(harness.connections).toHaveLength(0);
  });
});

// The SDK boundary the PATH case judges, replaced so the transport's own default environment
// contributes nothing: with it empty, a `PATH` entry in the default binding can have no source
// other than the plugin's own carry (T2, T17). `vi.mock` is hoisted over this file's module graph,
// so the replacement cannot be limited to the describe below; it changes no other export the
// adapter imports, and the binding cases below are the only ones that read this one.
vi.mock('@modelcontextprotocol/client/stdio', async () => {
  const actual =
    await vi.importActual<typeof import('@modelcontextprotocol/client/stdio')>(
      '@modelcontextprotocol/client/stdio',
    );
  return {
    ...actual,
    getDefaultEnvironment: (): Record<string, string> => ({}),
  };
});

// The binding the edge composes for itself when composition supplies no evaluator, read through
// the adapter's pure builder: no connection is created, so the interpreter and the transport
// environment are pinned without starting a process. Every expected value comes from the test
// factory, whose literal is independent of the plugin's own constant, so an expectation copied
// from the code under test cannot hide a changed command.
describe('plugin default connection binding', () => {
  // The inherited environment is installed by the case that judges it and removed here, so no
  // later case observes a value this group left behind and the outcome never depends on the
  // machine's own environment (T18).
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  test('names the node interpreter as the default connection command', () => {
    const { options, expectedCommand } = createDefaultConnectionExpectation();

    // The factory states the literal `node` itself; the plugin's own constant is not imported.
    expect(expectedCommand).toBe('node');
    expect(options.command).toBe(expectedCommand);
  });

  test('does not restart the host executable that cannot run the entry module', () => {
    const { options, forbiddenCommand } = createDefaultConnectionExpectation();

    // OpenCode runs on Bun, so `process.execPath` there is the host's own executable rather
    // than an interpreter started for this `.ts` entry.
    expect(forbiddenCommand).toBe(process.execPath);
    expect(options.command).not.toBe(process.execPath);
    expect(options.command).not.toBe(forbiddenCommand);
  });

  test('carries a non-empty PATH into the transport environment', () => {
    vi.stubEnv('PATH', STATED_PATH);

    // The replacement declared above is in force: with the inherited value installed, the SDK's
    // own default environment would have returned it, and the replaced one contributes nothing.
    // The entry asserted below therefore has no other source (T2, T17).
    expect(getDefaultEnvironment()).toStrictEqual({});

    const { options, requiredEnvironmentName } = createDefaultConnectionExpectation();

    expect(requiredEnvironmentName).toBe('PATH');
    // The transport spawns the child with its own filtered environment, so a bare executable
    // name is only resolvable when the inherited PATH travels explicitly. The SDK's default
    // environment supplies no PATH here, so the entry read below can only be the plugin's own
    // carry of the inherited value: a build that dropped that carry fails here instead of
    // passing on a value the SDK supplied.
    const path = options.env?.[requiredEnvironmentName];
    expect(typeof path).toBe('string');
    expect(path).not.toBe('');
    // The carried entry is exactly the inherited value this case stated: a filter that dropped
    // or rewrote it is observed, and no value read from the machine stands in for it.
    expect(path).toBe(STATED_PATH);
  });
});

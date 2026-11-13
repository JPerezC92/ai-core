/**
 * The shared runner for the parity corpus.
 *
 * One case is: materialise the synthetic fixture, run the case's commands
 * against the bound engine, compare each command's observable outcome with the
 * case's stated outcome, then compare the resulting filesystem tree with the
 * case's stated tree. Every difference is reported; the case fails when one
 * remains.
 */

import { resolveEngineUnderTest, type EngineUnderTest } from "./engine.ts";
import { REVISION, materialiseFixture } from "./fixtures.ts";
import { compareTree, snapshotTree } from "./tree.ts";
import type { ParityCase, StepExpectation } from "./types.ts";

/** Run one case and return the differences it produced; empty means it passed. */
export async function runParityCase(testCase: ParityCase): Promise<string[]> {
  const engine = await resolveEngineUnderTest();
  const fixture = await materialiseFixture(testCase.fixture);
  try {
    return await execute(engine, testCase, fixture);
  } finally {
    await fixture.dispose();
  }
}

async function execute(
  engine: EngineUnderTest,
  testCase: ParityCase,
  fixture: Awaited<ReturnType<typeof materialiseFixture>>,
): Promise<string[]> {
  const differences: string[] = [];

  if (testCase.steps.length !== testCase.expectations.length) {
    differences.push(
      `${testCase.id}: the case declares ${testCase.steps.length} command(s) and ${testCase.expectations.length} expectation(s)`,
    );
    return differences;
  }

  for (const [index, step] of testCase.steps.entries()) {
    const expectation = testCase.expectations[index];
    if (expectation === undefined) {
      continue;
    }
    const outcome = await engine.run({
      command: step.command,
      sourceRoot: fixture.sourceRoot,
      destinationRoot: fixture.destinationRoot,
      bindingsPath: fixture.bindingsPath,
      sourceRevision: step.revisionOverride ?? REVISION,
      bind: step.bind,
      bindRaw: step.bindRaw,
      bindCleared: step.bindCleared,
      root: step.root,
    });
    differences.push(...compareOutcome(engine, testCase, index, outcome, expectation));
  }

  const observedDestination = await snapshotTree(fixture.destinationRoot);
  differences.push(
    ...compareTree(fixture.destinationRoot, observedDestination, testCase.destinationTree),
  );

  if (testCase.sourceTree !== undefined) {
    const observedSource = await snapshotTree(fixture.sourceRoot);
    differences.push(...compareTree(fixture.sourceRoot, observedSource, testCase.sourceTree));
  }

  return differences;
}

function compareOutcome(
  engine: EngineUnderTest,
  testCase: ParityCase,
  index: number,
  outcome: { readonly exitCode: number; readonly stdout: string; readonly stderr: string },
  expectation: StepExpectation,
): string[] {
  const differences: string[] = [];
  const label = `${testCase.id} step ${index + 1} (${engine.id})`;
  if (outcome.exitCode !== expectation.exitCode) {
    differences.push(
      `${label}: exit code ${outcome.exitCode}, expected ${expectation.exitCode}\n--- stderr ---\n${outcome.stderr}\n--- end ---`,
    );
  }
  if (outcome.stdout !== expectation.stdout) {
    differences.push(
      `${label}: stdout differs\n--- expected ---\n${expectation.stdout}\n--- actual ---\n${outcome.stdout}\n--- end ---`,
    );
  }
  switch (expectation.stderr.kind) {
    case "empty":
      if (outcome.stderr !== "") {
        differences.push(`${label}: stderr is not empty\n--- actual ---\n${outcome.stderr}\n--- end ---`);
      }
      break;
    case "exact":
      if (outcome.stderr !== expectation.stderr.value) {
        differences.push(
          `${label}: stderr differs\n--- expected ---\n${expectation.stderr.value}\n--- actual ---\n${outcome.stderr}\n--- end ---`,
        );
      }
      break;
    case "contains":
      for (const required of expectation.stderr.value) {
        if (!outcome.stderr.includes(required)) {
          differences.push(
            `${label}: stderr does not mention ${JSON.stringify(required)}\n--- actual ---\n${outcome.stderr}\n--- end ---`,
          );
        }
      }
      break;
  }
  return differences;
}

# Behavioral-parity corpus for the TypeScript synchronization engine

This corpus states, in data, what the synchronization engine must produce. It
was authored from the documented contract — `.opencode/skills/core-sync/SKILL.md`
(`## Binding modes`, `## Marker contract`, `## Bindings schema`,
`## Reconciliation blocker`, `## Exit contract`, `## Commands`),
`.aicore/core/architecture/testing/architecture.md` and `.aicore/core/architecture/testing/stacks/typescript.md`
— **before** the TypeScript engine existed, so that parity is measured against
the contract instead of being produced by rewriting tests to fit an
implementation.

Every case names a synthetic fixture, a command, and the outcome that command
must produce. No case derives an expectation by running an engine.

## The interface an engine must expose

An engine is judged through one seam, `tests/support/core-sync-parity/engine.ts`:

```ts
export type EngineRequest = {
  readonly command: "check" | "apply" | "init";
  readonly sourceRoot: string;
  readonly destinationRoot: string;
  readonly bindingsPath: string;
  readonly sourceRevision: string;
  readonly bind?: readonly string[] | undefined;
  readonly bindRaw?: readonly string[] | undefined;
  readonly bindCleared?: boolean | undefined;
  readonly root?: string | undefined;
};

export type EngineOutcome = {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
};

export type EngineUnderTest = {
  readonly id: string;
  run(request: EngineRequest): Promise<EngineOutcome>;
};
```

The TypeScript engine must live at `cli/aicore/src/infrastructure/core-sync-engine.ts`
and export `createCoreSyncEngine(): EngineUnderTest`. The seam binds that module;
no case changes.

An engine is free to implement the commands however it likes. It must only
accept the request, perform the command over the given roots, and report the
exit status, standard output and standard error.

## What the comparison is

For each case the corpus:

1. materialises the synthetic source tree, destination tree, clearance registry
   and bindings document in a disposable temporary root;
2. runs the case's command(s) through the bound engine;
3. compares the **exit status**, **standard output** and **standard error**
   with the case's stated outcome, and
4. compares the **whole resulting filesystem tree** — every file, directory and
   symbolic link under the destination root — with the case's stated tree. A
   file the engine wrote that the case did not expect, or a file the case
   expected that the engine did not write, is a difference.

The source tree is compared too where the case says so: the source is read-only.

### How each written file is compared

| Kind | Comparison | Why |
|---|---|---|
| `file` | byte-for-byte | The contract fixes these bytes (region payloads, raw copies, the root runtime file). |
| `jsonc` | content, with layout whitespace removed | The contract fixes what a merge preserves "by content, not byte-for-byte". |
| `bindings` | the parsed document | The contract fixes the schema, not the YAML dialect. |
| `report` | the parsed document | The contract fixes the report's content, not its YAML dialect. |
| `blocker` | exact prefix and suffix, required facts in the body | The contract fixes the block's shape; its words are the reference's. |
| `directory`, `symlink` | kind and link target | The tree must contain exactly what the case states. |

## Layout

```
tests/support/core-sync-parity/
  types.ts               the corpus's data model
  corpus.ts              the case table — the corpus itself
  cases/
    binding-declarations.ts  the `--bind` / `--bind-raw` declaration cases
    root-role.ts             the `role: root` and `--root` destination-root cases
    clearance-integrity.ts   the duplicate-key clearance cases
  blocker.ts             the shipped blocker block (reference behaviour)
  fixtures.ts            the synthetic fixture builders
  engine.ts              the engine seam and its binding
  mini-yaml.ts           a reader for the two documents' YAML subset
  document.ts            the bindings and report projections
  tree.ts                the filesystem snapshot and comparison
  runner.ts              the shared case runner
  describe-concern.ts    the shared spec registration
tests/integration/core-sync-parity/
  region-mode.parity.spec.ts
  raw-mode.parity.spec.ts
  merge-mode.parity.spec.ts
  marker-contract.parity.spec.ts
  bindings-schema.parity.spec.ts
  exit-contract.parity.spec.ts
  safety-refusals.parity.spec.ts
  idempotence.parity.spec.ts
  binding-declarations.parity.spec.ts
  root-role.parity.spec.ts
  clearance-integrity.parity.spec.ts
```

One concern owns one spec file; the cases live in the corpus data module.

## Provenance

Each case carries a `provenance` block with two lists:

- `contract` — the governing text of the expectation.
- `reference` — behaviour the contract does not spell out, read from the Python
  reference engine: the diagnostic wording, the two YAML documents' exact
  serialization, the report's action words, and the shipped words of the
  blocker block.

A reference-sourced expectation is **reference behaviour, not contract text**.
It is flagged for the coordinator, and a TypeScript engine that differs must
change the corpus by an explicit decision, never silently.

## Reading the corpus

`pnpm --dir cli/aicore test` runs it. The seam binds the TypeScript engine, which
is the engine the corpus judges: it answers "what does the engine do with this
fixture", never "what should this fixture expect".

Three cases need a symbolic link. Windows refuses to create one without an
elevated privilege, so on such a machine those three are reported as skipped
rather than as covered; they run on a platform that allows them.

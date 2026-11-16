import { describe, expect, it } from 'vitest';

import { InitializeLocalRegisters } from '#scripts/incident_workflow_pkg/application/initialize_local_registers.ts';

const SYMPTOMS = 'incidents/diagnostics/symptoms.md';
const PROBLEMS = 'incidents/diagnostics/problems.md';
const SYMPTOMS_TEMPLATE = 'skill/references/local-symptoms-template.md';
const PROBLEMS_TEMPLATE = 'skill/references/local-problems-template.md';
const BASELINE = '.aicore/core/knowledge/diagnostics/symptoms.md';

const TEMPLATE_SYMPTOMS = '| ID | Symptom |\n|---|---|\n';
const TEMPLATE_PROBLEMS = '| ID | Date | Team | Symptom | System | Module | Problem | Discriminators | Exclusions | Evidence | Root cause | Lifecycle | Allow_exact | Status |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n';

/** A memory filesystem: the operation is pure over these ports. */
function makePorts(initial: Record<string, string> = {}) {
  const files = new Map(Object.entries(initial));
  const directories: string[] = [];
  return {
    files,
    directories,
    ports: {
      isFile: (path: string) => files.has(path),
      readText: (path: string) => {
        const value = files.get(path);
        if (value === undefined) throw new Error(`missing ${path}`);
        return value;
      },
      writeText: (path: string, content: string) => {
        files.set(path, content);
      },
      ensureDirectory: (path: string) => {
        directories.push(path);
      },
    },
  };
}

function request() {
  return {
    localSymptomsPath: SYMPTOMS,
    localProblemsPath: PROBLEMS,
    localSymptomsTemplate: SYMPTOMS_TEMPLATE,
    localProblemsTemplate: PROBLEMS_TEMPLATE,
    baselineSymptomsPath: BASELINE,
  };
}

function seedTemplates(): Record<string, string> {
  return {
    [SYMPTOMS_TEMPLATE]: TEMPLATE_SYMPTOMS,
    [PROBLEMS_TEMPLATE]: TEMPLATE_PROBLEMS,
    [BASELINE]: '| ID | Symptom |\n|---|---|\n| S-05 | Network |\n',
  };
}

describe('authorized register initialization', () => {
  it('creates both registers when neither exists', () => {
    const memory = makePorts(seedTemplates());
    const result = new InitializeLocalRegisters(memory.ports).execute(request());

    expect(result.created).toEqual([SYMPTOMS, PROBLEMS]);
    expect(result.kept).toEqual([]);
    expect(result.violations).toEqual([]);
    expect(memory.files.get(SYMPTOMS)).toBe(TEMPLATE_SYMPTOMS);
    expect(memory.files.get(PROBLEMS)).toBe(TEMPLATE_PROBLEMS);
    expect(memory.directories).toEqual(['incidents/diagnostics', 'incidents/diagnostics']);
  });

  it('never overwrites an existing register', () => {
    const existing = '| ID | Symptom |\n|---|---|\n| LOCAL:S-01 | mine |\n';
    const memory = makePorts({ ...seedTemplates(), [SYMPTOMS]: existing });
    const result = new InitializeLocalRegisters(memory.ports).execute(request());

    expect(result.created).toEqual([PROBLEMS]);
    expect(result.kept).toEqual([SYMPTOMS]);
    expect(memory.files.get(SYMPTOMS)).toBe(existing);
  });

  it('leaves both registers alone when both exist', () => {
    const symptoms = '| ID | Symptom |\n|---|---|\n| LOCAL:S-01 | mine |\n';
    const problems = '| ID | Date | Team | Symptom | System | Module | Problem | Discriminators | Exclusions | Evidence | Root cause | Lifecycle | Allow_exact | Status |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n';
    const memory = makePorts({ ...seedTemplates(), [SYMPTOMS]: symptoms, [PROBLEMS]: problems });
    const result = new InitializeLocalRegisters(memory.ports).execute(request());

    expect(result.created).toEqual([]);
    expect(result.kept).toEqual([SYMPTOMS, PROBLEMS]);
    expect(result.violations).toEqual([]);
  });

  it('reports a malformed existing register instead of repairing it', () => {
    const malformed = '| ID | Symptom |\n|---|---|\n| LOCAL:S-01 | duplicate |\n| LOCAL:S-01 | twice |\n';
    const memory = makePorts({ ...seedTemplates(), [SYMPTOMS]: malformed });
    const result = new InitializeLocalRegisters(memory.ports).execute(request());

    expect(result.violations).toEqual([
      'KNOWLEDGE-3: local symptom register defines an id twice: LOCAL:S-01',
    ]);
    expect(memory.files.get(SYMPTOMS)).toBe(malformed);
  });

  it('reports an incompatible existing register that reuses a baseline id', () => {
    const incompatible = '| ID | Symptom |\n|---|---|\n| S-05 | shadowed |\n';
    const memory = makePorts({ ...seedTemplates(), [SYMPTOMS]: incompatible });
    const result = new InitializeLocalRegisters(memory.ports).execute(request());

    expect(result.violations).toContain(
      'KNOWLEDGE-7: local register defines a non-LOCAL symptom id: S-05',
    );
    expect(memory.files.get(SYMPTOMS)).toBe(incompatible);
  });

  it('does not create registers during a read-only validation', () => {
    const memory = makePorts(seedTemplates());
    expect(memory.files.has(SYMPTOMS)).toBe(false);
    expect(memory.directories).toEqual([]);
  });
});

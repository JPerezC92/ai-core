#!/usr/bin/env node
/**
 * Authorized initialization entry point for a project's diagnostic registers.
 *
 * This is the runnable operation the incident workflow calls before a first
 * identification. It creates a missing register from its shipped template and
 * never rewrites one that exists; an existing malformed register is reported
 * and left untouched. Exit status: 0 created or kept with no defect, 1 a
 * reported defect, 2 usage.
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { InitializeLocalRegisters } from './incident_workflow_pkg/application/initialize_local_registers.ts';

const SKILL_ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

function usage(): void {
  console.error('usage: init_local_registers.ts <repo-root>');
}

function main(argv: readonly string[]): number {
  if (argv.includes('--help') || argv.includes('-h')) {
    usage();
    return 2;
  }
  const repoRoot = argv.find((argument) => !argument.startsWith('-')) ?? '.';
  /** Resolve a port path against the repo root unless it is already absolute. */
  const resolve = (path: string): string => (isAbsolute(path) ? path : join(repoRoot, path));
  const localSymptomsPath = 'incidents/diagnostics/symptoms.md';
  const localProblemsPath = 'incidents/diagnostics/problems.md';

  const result = new InitializeLocalRegisters({
    isFile: (path) => existsSync(resolve(path)),
    readText: (path) => readFileSync(resolve(path), 'utf8'),
    writeText: (path, content) => {
      writeFileSync(resolve(path), content, 'utf8');
    },
    ensureDirectory: (path) => {
      mkdirSync(resolve(path), { recursive: true });
    },
  }).execute({
    localSymptomsPath,
    localProblemsPath,
    localSymptomsTemplate: join(SKILL_ROOT, 'references', 'local-symptoms-template.md'),
    localProblemsTemplate: join(SKILL_ROOT, 'references', 'local-problems-template.md'),
    baselineSymptomsPath: '.aicore/core/knowledge/diagnostics/symptoms.md',
  });

  for (const path of result.created) console.log(`created ${path}`);
  for (const path of result.kept) console.log(`kept ${path}`);
  for (const violation of result.violations) console.error(violation);
  return result.violations.length === 0 ? 0 : 1;
}

process.exitCode = main(process.argv.slice(2));

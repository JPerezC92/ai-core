#!/usr/bin/env node
import { readFileSync } from 'node:fs';

import { serveStdio } from '@modelcontextprotocol/server/stdio';

import { DumpSyntaxTree } from '#application/dump-syntax-tree.ts';
import { FindCode } from '#application/find-code.ts';
import { FindCodeByRule } from '#application/find-code-by-rule.ts';
import { TestMatchCodeRule } from '#application/test-match-code-rule.ts';
import { AstGrepProcess } from '#infrastructure/adapters/ast-grep-process.ts';
import { createAstGrepServer, languageListFromConfigText } from './ast-grep-server.ts';

if (typeof process.on === 'function') {
  process.on('SIGINT', () => {
    process.stderr.write('Received SIGINT - ignoring for multi-session stability\n');
  });
}

const configPath = readConfigPath(process.env);
const commandPrefix = process.env.AST_GREP_PATH?.trim() || 'ast-grep';
const configYaml = configPath === undefined ? undefined : readFileSync(configPath, 'utf8');
const cli = new AstGrepProcess({
  commandPrefix,
  configPath,
  platform: process.platform,
});
const languages = languageListFromConfigText(configYaml);

serveStdio(
  () =>
    createAstGrepServer(
      {
        dumpSyntaxTree: new DumpSyntaxTree(cli),
        findCode: new FindCode(cli),
        findCodeByRule: new FindCodeByRule(cli),
        testMatchCodeRule: new TestMatchCodeRule(cli),
      },
      languages,
    ),
  {
    onerror: (error) => {
      process.stderr.write(`ast-grep-mcp: ${error.name}: ${error.message}\n`);
    },
  },
);

function readConfigPath(environment: NodeJS.ProcessEnv): string | undefined {
  const fromEnv = environment.AST_GREP_CONFIG?.trim();
  return fromEnv === undefined || fromEnv.length === 0 ? undefined : fromEnv;
}

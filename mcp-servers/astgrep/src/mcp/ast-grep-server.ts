import { McpServer } from '@modelcontextprotocol/server';
import { z } from 'zod';

import type { DumpSyntaxTree } from '../application/dump-syntax-tree.ts';
import type { FindCode } from '../application/find-code.ts';
import type { FindCodeByRule } from '../application/find-code-by-rule.ts';
import type { TestMatchCodeRule } from '../application/test-match-code-rule.ts';
import { isAstGrepError } from '../domain/errors.ts';
import { supportedLanguages } from '../domain/languages.ts';
import type { MatchRecord } from '../domain/matches.ts';

export type AstGrepOperations = {
  readonly dumpSyntaxTree: DumpSyntaxTree;
  readonly findCode: FindCode;
  readonly findCodeByRule: FindCodeByRule;
  readonly testMatchCodeRule: TestMatchCodeRule;
};

export function createAstGrepServer(
  operations: AstGrepOperations,
  languageList: readonly string[],
): McpServer {
  const languages = languageList.join(', ');
  const server = new McpServer({ name: 'ast-grep', version: '0.1.0' });

  server.registerTool(
    'dump_syntax_tree',
    {
      title: 'Dump syntax tree',
      description:
        "Dump code's syntax structure or dump a query's pattern structure. Internally calls: ast-grep run --pattern <code> --lang <language> --debug-query=<format>",
      inputSchema: z.object({
        code: z.string().describe('The code you need'),
        language: z.string().describe(`The language of the code. Supported: ${languages}`),
        format: z
          .enum(['pattern', 'cst', 'ast'])
          .default('cst')
          .describe('Code dump format. Available values: pattern, ast, cst'),
      }),
    },
    async ({ code, language, format }) => {
      const text = await operations.dumpSyntaxTree.execute({ code, language, format });
      return { content: [{ type: 'text' as const, text }] };
    },
  );

  server.registerTool(
    'find_code',
    {
      title: 'Find code',
      description:
        'Find code in a project folder that matches the given ast-grep pattern. Internally calls: ast-grep run --pattern <pattern> [--lang] --json=stream <project_folder>',
      inputSchema: z.object({
        project_folder: z
          .string()
          .describe('The absolute path to the project folder. It must be absolute path.'),
        pattern: z.string().describe('The ast-grep pattern to search for.'),
        language: z
          .string()
          .default('')
          .describe(
            `The language of the code. Supported: ${languages}. If not specified, will be auto-detected based on file extensions.`,
          ),
        max_results: z.number().int().default(0).describe('Maximum results to return'),
        output_format: z.string().default('text').describe("'text' or 'json'"),
      }),
    },
    async ({ project_folder, pattern, language, max_results, output_format }) => {
      const result = await operations.findCode.execute({
        projectFolder: project_folder,
        pattern,
        language,
        maxResults: max_results,
        outputFormat: output_format,
      });
      return serializeFind(result, max_results);
    },
  );

  server.registerTool(
    'find_code_by_rule',
    {
      title: 'Find code by rule',
      description:
        "Find code using ast-grep's YAML rule in a project folder. Internally calls: ast-grep scan --inline-rules <yaml> --json=stream <project_folder>",
      inputSchema: z.object({
        project_folder: z
          .string()
          .describe('The absolute path to the project folder. It must be absolute path.'),
        yaml: z
          .string()
          .describe('The ast-grep YAML rule to search. It must have id, language, rule fields.'),
        max_results: z.number().int().default(0).describe('Maximum results to return'),
        output_format: z.string().default('text').describe("'text' or 'json'"),
      }),
    },
    async ({ project_folder, yaml, max_results, output_format }) => {
      const result = await operations.findCodeByRule.execute({
        projectFolder: project_folder,
        yaml,
        maxResults: max_results,
        outputFormat: output_format,
      });
      return serializeFind(result, max_results);
    },
  );

  server.registerTool(
    'test_match_code_rule',
    {
      title: 'Test match code rule',
      description:
        'Test a code against an ast-grep YAML rule. Internally calls: ast-grep scan --inline-rules <yaml> --json --stdin',
      inputSchema: z.object({
        code: z.string().describe('The code to test against the rule'),
        yaml: z
          .string()
          .describe('The ast-grep YAML rule to search. It must have id, language, rule fields.'),
      }),
    },
    async ({ code, yaml }) => {
      const matches = await operations.testMatchCodeRule.execute({ code, yaml });
      if (isAstGrepError(matches)) {
        return {
          content: [{ type: 'text' as const, text: matches.message }],
          isError: true,
        };
      }
      return {
        content: [{ type: 'text' as const, text: JSON.stringify(matches) }],
        structuredContent: { matches },
      };
    },
  );

  return server;
}

export function languageListFromConfigText(configYaml: string | undefined): string[] {
  return supportedLanguages(configYaml);
}

function serializeFind(
  result:
    | {
        readonly matches: MatchRecord[];
        readonly totalMatches: number;
        readonly outputFormat: 'text' | 'json';
      }
    | { readonly code: string; readonly message: string },
  maxResults: number,
) {
  if (isAstGrepError(result)) {
    return {
      content: [{ type: 'text' as const, text: result.message }],
      isError: true,
    };
  }
  if (result.outputFormat === 'text') {
    return {
      content: [
        {
          type: 'text' as const,
          text: formatFindText(result.matches, result.totalMatches, maxResults),
        },
      ],
    };
  }
  return {
    content: [{ type: 'text' as const, text: JSON.stringify(result.matches) }],
    structuredContent: { matches: result.matches },
  };
}

function formatFindText(
  matches: readonly MatchRecord[],
  totalMatches: number,
  maxResults: number,
): string {
  if (matches.length === 0) {
    return 'No matches found';
  }
  let header = `Found ${matches.length} matches`;
  if (maxResults && totalMatches > maxResults) {
    header += ` (showing first ${maxResults} of ${totalMatches})`;
  }
  return `${header}:\n\n${formatMatchesAsText(matches)}`;
}

function formatMatchesAsText(matches: readonly MatchRecord[]): string {
  if (matches.length === 0) {
    return '';
  }
  const blocks: string[] = [];
  for (const match of matches) {
    const startLine = match.range.start.line + 1;
    const endLine = match.range.end.line + 1;
    const matchText = match.text.replace(/[\r\n]+$/u, '');
    const header =
      startLine === endLine ? `${match.file}:${startLine}` : `${match.file}:${startLine}-${endLine}`;
    blocks.push(`${header}\n${matchText}`);
  }
  return blocks.join('\n\n');
}

import { McpServer } from '@modelcontextprotocol/server';
import { z } from 'zod';

import type { AstGrepTools } from '../application/ast-grep-tools.ts';
import { supportedLanguages } from '../domain/languages.ts';

export function createAstGrepServer(
  tools: AstGrepTools,
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
      const text = await tools.dumpSyntaxTree(code, language, format);
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
      const result = await tools.findCode(
        project_folder,
        pattern,
        language,
        max_results,
        output_format,
      );
      return jsonOrText(result);
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
      const result = await tools.findCodeByRule(
        project_folder,
        yaml,
        max_results,
        output_format,
      );
      return jsonOrText(result);
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
      const matches = await tools.testMatchCodeRule(code, yaml);
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

function jsonOrText(result: string | unknown[]) {
  if (typeof result === 'string') {
    return { content: [{ type: 'text' as const, text: result }] };
  }
  return {
    content: [{ type: 'text' as const, text: JSON.stringify(result) }],
    structuredContent: { matches: result },
  };
}

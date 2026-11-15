import { spawn } from 'node:child_process';

import { isNoMatchExit } from '#domain/exit-code.ts';
import type { MatchRecord } from '#domain/matches.ts';
import type { AstGrepCli, CliResult, MatchList } from '#domain/ports.ts';
import { resolveSpawnFile, splitCommandPrefix } from '#infrastructure/command-prefix.ts';

export type ProcessResult = CliResult;

export type AstGrepProcessOptions = {
  readonly commandPrefix: string;
  readonly configPath: string | undefined;
  readonly platform: NodeJS.Platform;
};

export class AstGrepProcess implements AstGrepCli {
  private readonly options: AstGrepProcessOptions;

  constructor(options: AstGrepProcessOptions) {
    this.options = options;
  }

  async dumpQuery(code: string, language: string, format: string): Promise<string> {
    const result = await this.run('run', [
      '--pattern',
      code,
      '--lang',
      language,
      `--debug-query=${format}`,
    ]);
    return result.stderr.trim();
  }

  async searchPattern(
    projectFolder: string,
    pattern: string,
    language: string,
  ): Promise<MatchList> {
    const args = ['--pattern', pattern];
    if (language.length > 0) {
      args.push('--lang', language);
    }
    const result = await this.run('run', [...args, '--json=stream', projectFolder]);
    return parseJsonlMatches(result.stdout);
  }

  async searchRule(projectFolder: string, yaml: string): Promise<MatchList> {
    const result = await this.run('scan', [
      '--inline-rules',
      yaml,
      '--json=stream',
      projectFolder,
    ]);
    return parseJsonlMatches(result.stdout);
  }

  async matchRuleOnCode(code: string, yaml: string): Promise<MatchRecord[]> {
    const result = await this.run(
      'scan',
      ['--inline-rules', yaml, '--json', '--stdin'],
      code,
    );
    const parsed = JSON.parse(result.stdout.trim() || '[]') as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.map((row) => toMatchRecord(row));
  }

  private async run(
    subcommand: string,
    args: readonly string[],
    inputText?: string,
  ): Promise<ProcessResult> {
    const prefixed = this.options.configPath
      ? ['--config', this.options.configPath, ...args]
      : [...args];
    return this.runCommand([this.options.commandPrefix, subcommand, ...prefixed], inputText);
  }

  private async runCommand(args: readonly string[], inputText?: string): Promise<ProcessResult> {
    const prefix = splitCommandPrefix(args[0] ?? '', this.options.platform);
    const argv = resolveSpawnFile([...prefix, ...args.slice(1)], this.options.platform);
    const result = await this.spawnOnce(argv, inputText);
    if (result.returncode !== 0) {
      if (isNoMatchExit(result.returncode, result.stdout, argv)) {
        return result;
      }
      const stderrMsg = result.stderr.trim() || '(no error output)';
      throw new Error(
        `Command ${JSON.stringify(argv)} failed with exit code ${result.returncode}: ${stderrMsg}`,
      );
    }
    return result;
  }

  private spawnOnce(argv: readonly string[], inputText: string | undefined): Promise<ProcessResult> {
    const file = argv[0];
    if (file === undefined) {
      return Promise.reject(new Error('AST_GREP_PATH must not be empty'));
    }
    return new Promise((resolve, reject) => {
      const child = spawn(file, argv.slice(1), {
        shell: false,
        windowsHide: true,
      });
      let stdout = '';
      let stderr = '';
      child.stdout.setEncoding('utf8');
      child.stderr.setEncoding('utf8');
      child.stdout.on('data', (chunk: string) => {
        stdout += chunk;
      });
      child.stderr.on('data', (chunk: string) => {
        stderr += chunk;
      });
      child.on('error', (error) => {
        if (error.message.includes('ENOENT') || (error as NodeJS.ErrnoException).code === 'ENOENT') {
          reject(
            new Error(
              `Command '${file}' not found. Please ensure ${file} is installed and in PATH.`,
            ),
          );
          return;
        }
        reject(error);
      });
      child.on('close', (code) => {
        resolve({ stdout, stderr, returncode: code ?? 1 });
      });
      if (inputText !== undefined) {
        child.stdin.end(inputText, 'utf8');
      } else {
        child.stdin.end();
      }
    });
  }
}

function parseJsonlMatches(stdout: string): MatchList {
  const matches: MatchRecord[] = [];
  let totalLines = 0;
  for (const raw of stdout.split(/\r?\n/)) {
    const line = raw.trim();
    if (line.length === 0 || !line.startsWith('{')) {
      continue;
    }
    totalLines += 1;
    matches.push(toMatchRecord(JSON.parse(line) as unknown));
  }
  return { matches, totalMatches: totalLines };
}

function toMatchRecord(row: unknown): MatchRecord {
  const record = row !== null && typeof row === 'object' ? (row as Record<string, unknown>) : {};
  const rangeRaw = record.range;
  const rangeObj =
    rangeRaw !== null && typeof rangeRaw === 'object' ? (rangeRaw as Record<string, unknown>) : {};
  return {
    file: typeof record.file === 'string' ? record.file : '',
    range: {
      start: { line: nestedLine(rangeObj, 'start') },
      end: { line: nestedLine(rangeObj, 'end') },
    },
    text: typeof record.text === 'string' ? record.text : '',
  };
}

function nestedLine(range: Record<string, unknown>, key: 'start' | 'end'): number {
  const side = range[key];
  if (side && typeof side === 'object' && side !== null && 'line' in side) {
    const line = (side as { line?: unknown }).line;
    return typeof line === 'number' ? line : 0;
  }
  return 0;
}

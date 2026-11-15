import { spawn } from 'node:child_process';
import { isNoMatchExit } from '../domain/exit-code.ts';
import type { AstGrepCli, CliResult } from '../domain/ports.ts';
import { resolveSpawnFile, splitCommandPrefix } from './command-prefix.ts';

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

  async run(
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
      throw new Error(`Command ${JSON.stringify(argv)} failed with exit code ${result.returncode}: ${stderrMsg}`);
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

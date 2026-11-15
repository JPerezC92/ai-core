export type CliResult = {
  readonly stdout: string;
  readonly stderr: string;
  readonly returncode: number;
};

export type AstGrepCli = {
  run(
    subcommand: string,
    args: readonly string[],
    inputText?: string,
  ): Promise<CliResult>;
};

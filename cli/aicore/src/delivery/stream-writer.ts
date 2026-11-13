/**
 * Delivery: writing rendered lines to the operator's terminal.
 *
 * The single place the process streams are touched.
 */

export interface StreamWriter {
  writeStdout(lines: readonly string[]): void;
  writeStderr(lines: readonly string[]): void;
}

export class ConsoleStreamWriter implements StreamWriter {
  writeStdout(lines: readonly string[]): void {
    for (const line of lines) {
      process.stdout.write(`${line}\n`);
    }
  }

  writeStderr(lines: readonly string[]): void {
    for (const line of lines) {
      process.stderr.write(`${line}\n`);
    }
  }
}

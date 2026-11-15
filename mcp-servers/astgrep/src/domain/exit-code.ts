export function isNoMatchExit(
  returnCode: number,
  stdout: string,
  argv: readonly string[],
): boolean {
  if (returnCode === 0) {
    return false;
  }
  if (returnCode !== 1) {
    return false;
  }
  const stdoutStripped = stdout.trim();
  if (
    stdoutStripped === '' ||
    stdoutStripped === '[]' ||
    stdoutStripped.startsWith('[') ||
    stdoutStripped.startsWith('{')
  ) {
    return true;
  }
  if (!argv.includes('--json') && stdoutStripped === '') {
    return true;
  }
  return false;
}

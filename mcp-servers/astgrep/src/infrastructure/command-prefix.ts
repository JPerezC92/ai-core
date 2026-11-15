export function splitCommandPrefix(raw: string, platform: NodeJS.Platform): string[] {
  if (raw.trim().length === 0) {
    throw new Error('AST_GREP_PATH must not be empty');
  }
  const posix = platform !== 'win32';
  const parts = posixSplit(raw, posix);
  if (platform === 'win32') {
    return parts.map((part) =>
      part.length >= 2 && part.startsWith('"') && part.endsWith('"')
        ? part.slice(1, -1)
        : part,
    );
  }
  return parts;
}

export function resolveSpawnFile(
  command: readonly string[],
  platform: NodeJS.Platform,
): string[] {
  if (platform === 'win32' && command[0] === 'ast-grep') {
    return ['ast-grep.exe', ...command.slice(1)];
  }
  return [...command];
}

function posixSplit(input: string, posix: boolean): string[] {
  const result: string[] = [];
  let current = '';
  let quote: '"' | "'" | null = null;
  let escape = false;
  for (const char of input) {
    if (escape) {
      current += char;
      escape = false;
      continue;
    }
    if (posix && char === '\\' && quote !== "'") {
      escape = true;
      continue;
    }
    if (quote === null) {
      if (char === '"' || (posix && char === "'")) {
        quote = char;
        if (!posix) {
          current += char;
        }
        continue;
      }
      if (/\s/u.test(char)) {
        if (current.length > 0) {
          result.push(current);
          current = '';
        }
        continue;
      }
      current += char;
      continue;
    }
    if (char === quote) {
      if (!posix) {
        current += char;
      }
      quote = null;
      continue;
    }
    current += char;
  }
  if (current.length > 0) {
    result.push(current);
  }
  if (result.length === 0) {
    throw new Error('AST_GREP_PATH must not be empty');
  }
  return result;
}

export const BUILTIN_LANGUAGES = [
  'bash',
  'c',
  'cpp',
  'csharp',
  'css',
  'elixir',
  'go',
  'haskell',
  'html',
  'java',
  'javascript',
  'json',
  'jsx',
  'kotlin',
  'lua',
  'nix',
  'php',
  'python',
  'ruby',
  'rust',
  'scala',
  'solidity',
  'swift',
  'tsx',
  'typescript',
  'yaml',
] as const;

export function customLanguageKeysFromConfig(yamlText: string): string[] {
  const lines = yamlText.split(/\r?\n/);
  const keys: string[] = [];
  let inCustom = false;
  let customIndent = 0;
  for (const line of lines) {
    if (!inCustom) {
      const match = /^( *)customLanguages\s*:/.exec(line);
      if (match) {
        inCustom = true;
        customIndent = match[1]?.length ?? 0;
      }
      continue;
    }
    if (line.trim().length === 0 || line.trimStart().startsWith('#')) {
      continue;
    }
    const indent = /^( *)/.exec(line)?.[1]?.length ?? 0;
    if (indent <= customIndent) {
      break;
    }
    const key = /^(?: *)([A-Za-z0-9_-]+)\s*:/.exec(line);
    if (key?.[1] !== undefined && indent === customIndent + 2) {
      keys.push(key[1]);
    }
  }
  return keys;
}

export function supportedLanguages(configYaml: string | undefined): string[] {
  const languages = new Set<string>(BUILTIN_LANGUAGES);
  if (configYaml !== undefined) {
    for (const key of customLanguageKeysFromConfig(configYaml)) {
      languages.add(key);
    }
  }
  return [...languages].sort();
}

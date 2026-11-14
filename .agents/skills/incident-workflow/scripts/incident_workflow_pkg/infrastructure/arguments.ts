export type ValidatorMode =
  | { readonly kind: 'analysis' }
  | { readonly kind: 'scaffold' }
  | { readonly kind: 'step'; readonly step: 'identify' | 'investigate' | 'synthesize' }
  | { readonly kind: 'pre-close' }
  | { readonly kind: 'close-out' };

export interface ValidatorArguments {
  readonly analysisDir: string;
  readonly repoRoot: string;
  readonly mode: ValidatorMode;
}

export type ArgumentResult =
  | { readonly kind: 'parsed'; readonly value: ValidatorArguments }
  | { readonly kind: 'help' }
  | { readonly kind: 'error'; readonly message: string };

const options = ['--help', '--step', '--scaffold', '--pre-close', '--close-out', '--repo-root'] as const;

export function parseArguments(args: readonly string[]): ArgumentResult {
  let analysisDir: string | undefined;
  let repoRoot = '.';
  let mode: ValidatorMode = { kind: 'analysis' };
  let selectedOption: string | undefined;
  const extra: string[] = [];

  for (let index = 0; index < args.length; index++) {
    const arg = args[index];
    if (arg === undefined) continue;
    if (arg === '--') {
      for (const positional of args.slice(index + 1)) {
        if (analysisDir === undefined) analysisDir = positional;
        else extra.push(positional);
      }
      break;
    }
    if (arg === '-h') return { kind: 'help' };
    if (!arg.startsWith('-') || arg === '-') {
      if (analysisDir === undefined) analysisDir = arg;
      else extra.push(arg);
      continue;
    }

    const separator = arg.indexOf('=');
    const spelling = separator < 0 ? arg : arg.slice(0, separator);
    const matches = options.filter(option => option.startsWith(spelling));
    if (matches.length > 1 && !matches.includes(spelling as typeof options[number])) {
      return { kind: 'error', message: `ambiguous option: ${spelling} could match ${matches.join(', ')}` };
    }
    const option = matches.find(item => item === spelling) ?? matches[0];
    if (option === undefined) {
      extra.push(arg);
      continue;
    }
    const inline = separator < 0 ? undefined : arg.slice(separator + 1);
    if (option === '--help' || option === '--scaffold' || option === '--pre-close' || option === '--close-out') {
      if (inline !== undefined) return { kind: 'error', message: `argument ${option}: ignored explicit argument '${inline}'` };
      if (option === '--help') return { kind: 'help' };
      if (selectedOption !== undefined && selectedOption !== option) {
        return { kind: 'error', message: `argument ${option}: not allowed with argument ${selectedOption}` };
      }
      selectedOption = option;
      mode = { kind: option.slice(2) as 'scaffold' | 'pre-close' | 'close-out' };
      continue;
    }

    let value = inline;
    if (value === undefined) {
      const next = args[index + 1];
      if (next === undefined || (next.startsWith('-') && next !== '-')) {
        return { kind: 'error', message: `argument ${option}: expected one argument` };
      }
      value = next;
      index++;
    }
    if (option === '--repo-root') {
      repoRoot = value;
      continue;
    }
    if (value !== 'identify' && value !== 'investigate' && value !== 'synthesize') {
      return { kind: 'error', message: `argument --step: invalid choice: '${value}' (choose from 'identify', 'investigate', 'synthesize')` };
    }
    if (selectedOption !== undefined && selectedOption !== option) {
      return { kind: 'error', message: `argument ${option}: not allowed with argument ${selectedOption}` };
    }
    selectedOption = option;
    mode = { kind: 'step', step: value };
  }

  if (analysisDir === undefined) return { kind: 'error', message: 'the following arguments are required: analysis_dir' };
  if (extra.length > 0) return { kind: 'error', message: `unrecognized arguments: ${extra.join(' ')}` };
  return { kind: 'parsed', value: { analysisDir, repoRoot, mode } };
}

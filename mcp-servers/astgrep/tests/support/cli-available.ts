import { spawnSync } from 'node:child_process';

export function astGrepAvailable(): boolean {
  const result = spawnSync('ast-grep', ['--version'], {
    encoding: 'utf8',
    shell: process.platform === 'win32',
  });
  return result.status === 0;
}

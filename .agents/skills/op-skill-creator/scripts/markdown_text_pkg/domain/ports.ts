/** Ports the application operation depends on; adapters live in infrastructure. */

import type { DiscoverResult, DomainError, FileTarget, Policy } from './models.ts';

export interface PolicyPort {
  load(path: string): Policy | DomainError;
}

export interface FilePort {
  discover(roots: readonly string[]): DiscoverResult;
  readBytes(target: FileTarget): Uint8Array | DomainError;
  loadJsonObject(path: string): Record<string, unknown> | DomainError;
}

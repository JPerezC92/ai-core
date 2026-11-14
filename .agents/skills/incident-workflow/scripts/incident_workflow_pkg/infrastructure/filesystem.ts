import { readFileSync, readdirSync, realpathSync, statSync } from 'node:fs';
import { dirname, isAbsolute, join, relative, sep } from 'node:path';

import type { CloseOutSnapshot, IncidentFiles } from '#scripts/incident_workflow_pkg/domain/ports.ts';
import { REQUIRED_ANALYSIS_FILES, STEP_FILES } from '#scripts/incident_workflow_pkg/domain/rules.ts';

function statOrMissing(path: string) {
  try {
    return statSync(path);
  } catch (error) {
    if (typeof error === 'object' && error !== null && 'code' in error && (error.code === 'ENOENT' || error.code === 'ENOTDIR')) return undefined;
    throw error;
  }
}

function inside(root: string, candidate: string): boolean {
  const path = relative(root, candidate);
  return path === '' || (path !== '..' && !path.startsWith(`..${sep}`) && !isAbsolute(path));
}

function resolveCitation(root: string, value: string): string {
  let current = root;
  const parts = sep === '\\' ? value.split(/[\\/]/) : value.split('/');
  for (const part of parts) {
    if (part === '' || part === '.') continue;
    if (part === '..') {
      current = dirname(current);
      continue;
    }
    const candidate = join(current, part);
    try {
      current = realpathSync(candidate);
    } catch (error) {
      if (typeof error !== 'object' || error === null || !('code' in error) || (error.code !== 'ENOENT' && error.code !== 'ENOTDIR')) throw error;
      current = candidate;
    }
  }
  return current;
}

function citedPaths(content: string): string[] {
  const withoutComments = content.replace(/<!--[\s\S]*?-->/g, '');
  return [...withoutComments.matchAll(/\bpath:\s*\**\s*([^\n]+)/g)]
    .map(match => (match[1] ?? '').trim().replace(/^`+|`+$/g, '').trim())
    .filter(Boolean);
}

function downloadsUnder(root: string): string[] {
  const downloads = join(root, 'downloads');
  if (!statOrMissing(downloads)?.isDirectory()) return [];
  const found: string[] = [];
  function visit(directory: string): void {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      else if (statOrMissing(path)?.isFile()) found.push(relative(root, path).split(sep).join('/'));
    }
  }
  visit(downloads);
  return found.sort();
}

function directoryEntries(path: string): string[] {
  return statOrMissing(path)?.isDirectory() ? readdirSync(path) : [];
}

export class Filesystem implements IncidentFiles {
  readText(path: string): string {
    return readFileSync(path, 'utf8');
  }

  isFile(path: string): boolean {
    return statOrMissing(path)?.isFile() ?? false;
  }

  loadStepFiles(analysisDir: string): Record<string, string> {
    const contents: Record<string, string> = {};
    for (const name of STEP_FILES) {
      const path = join(analysisDir, name);
      if (this.isFile(path)) contents[name] = this.readText(path);
    }
    return contents;
  }

  loadCloseOutSnapshot(ticketDir: string): CloseOutSnapshot {
    const analysisDir = join(ticketDir, 'analysis');
    const workingAnalysisFiles = directoryEntries(analysisDir)
      .filter(name => name.endsWith('.md') && this.isFile(join(analysisDir, name))).sort();
    const analysisContents: Record<string, string> = {};
    for (const name of REQUIRED_ANALYSIS_FILES) {
      const path = join(analysisDir, name);
      if (this.isFile(path)) analysisContents[name] = this.readText(path);
    }
    const ticketFileNames = directoryEntries(ticketDir)
      .filter(name => /^ticket_.*\.md$/.test(name) && this.isFile(join(ticketDir, name))).sort();
    const ticketContent = ticketFileNames.length === 1 ? this.readText(join(ticketDir, ticketFileNames[0]!)) : null;
    const citations = ticketContent === null ? [] : citedPaths(ticketContent);
    const missingImagePaths: string[] = [];
    const missingTicketPaths: string[] = [];
    const unsafeTicketPaths: string[] = [];
    if (citations.length > 0) {
      const root = realpathSync(ticketDir);
      for (const value of citations) {
        const candidate = isAbsolute(value) ? value : resolveCitation(root, value);
        const unsafe = isAbsolute(value) || !inside(root, candidate);
        const exists = !unsafe && this.isFile(candidate);
        if (unsafe) {
          unsafeTicketPaths.push(value);
          missingImagePaths.push(value);
        } else if (!exists) {
          missingTicketPaths.push(value);
          missingImagePaths.push(value);
        }
      }
    }
    return {
      ticketFileNames, ticketContent, citedPaths: citations, workingAnalysisFiles, analysisContents,
      responseDraftPresent: this.isFile(join(ticketDir, 'response-draft.md')),
      screenshotsDirPresent: statOrMissing(join(ticketDir, 'screenshots'))?.isDirectory() ?? false,
      validationsDirPresent: statOrMissing(join(ticketDir, 'validations'))?.isDirectory() ?? false,
      missingImagePaths, missingTicketPaths, unsafeTicketPaths,
      leftoverDownloadFiles: downloadsUnder(ticketDir),
    };
  }
}

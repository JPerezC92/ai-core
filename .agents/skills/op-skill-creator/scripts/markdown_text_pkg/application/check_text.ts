/** Markdown text-integrity use case: one execute() with injected policy and file ports. */

import type { CheckOutcome, DomainError, Finding } from '#scripts/markdown_text_pkg/domain/models.ts';
import { isDomainError } from '#scripts/markdown_text_pkg/domain/models.ts';
import type { FilePort, PolicyPort } from '#scripts/markdown_text_pkg/domain/ports.ts';
import { compareEditorProjection } from '#scripts/markdown_text_pkg/domain/policy.ts';
import { scanMarkdownBytes } from '#scripts/markdown_text_pkg/domain/scan.ts';

function compareFindings(left: Finding, right: Finding): number {
  if (left.path !== right.path) return left.path < right.path ? -1 : 1;
  if (left.kind === 'editor-drift' || right.kind === 'editor-drift') return left.kind === right.kind ? 0 : 1;
  if (left.line !== right.line) return left.line - right.line;
  if (left.column !== right.column) return left.column - right.column;
  return left.ruleId < right.ruleId ? -1 : left.ruleId > right.ruleId ? 1 : 0;
}

function compareFailures(left: DomainError, right: DomainError): number {
  if (left.code !== right.code) return left.code < right.code ? -1 : 1;
  return left.message < right.message ? -1 : left.message > right.message ? 1 : 0;
}

export class CheckText {
  readonly #policyPort: PolicyPort;
  readonly #filePort: FilePort;

  constructor(policyPort: PolicyPort, filePort: FilePort) {
    this.#policyPort = policyPort;
    this.#filePort = filePort;
  }

  /** Return typed findings and failures; never serializes or prints. */
  execute(policyPath: string, roots: readonly string[], editorPath: string | null): CheckOutcome {
    const policy = this.#policyPort.load(policyPath);
    if (isDomainError(policy)) return { findings: [], failures: [policy] };

    const discovered = this.#filePort.discover(roots);
    const failures: DomainError[] = [...discovered.failures];
    const findings: Finding[] = [];

    for (const target of discovered.targets) {
      const payload = this.#filePort.readBytes(target);
      if (isDomainError(payload)) {
        failures.push(payload);
        continue;
      }
      findings.push(...scanMarkdownBytes(payload, policy, target.displayPath));
    }

    if (editorPath !== null) {
      const settings = this.#filePort.loadJsonObject(editorPath);
      if (isDomainError(settings)) {
        failures.push(settings);
      } else {
        const drift = compareEditorProjection(policy, settings, editorPath);
        if (isDomainError(drift)) failures.push(drift);
        else if (drift !== undefined) findings.push(drift);
      }
    }

    return {
      findings: [...findings].sort(compareFindings),
      failures: [...failures].sort(compareFailures),
    };
  }
}

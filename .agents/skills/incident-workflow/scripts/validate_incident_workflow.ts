import { basename } from 'node:path';

import { runValidator } from '#scripts/incident_workflow_pkg/entry.ts';
import { parseArguments } from '#scripts/incident_workflow_pkg/infrastructure/arguments.ts';

const program = basename(process.argv[1] ?? 'validate_incident_workflow.ts');
const usage = `usage: ${program} [-h] [--step {identify,investigate,synthesize} | --scaffold | --pre-close | --close-out] [--repo-root REPO_ROOT] analysis_dir`;
const parsed = parseArguments(process.argv.slice(2));
if (parsed.kind === 'error') {
  console.error(`${usage}\n${program}: error: ${parsed.message}`);
  process.exitCode = 2;
} else if (parsed.kind === 'help') {
  console.log(`${usage}\n\nValidate a ticket working-analysis directory (state.md + steps) and its closed-out ticket set.\n\nDefault: validate completed steps through the header Phase value.\nWith --scaffold: structural-only validation of all copied steps.\nWith --step NAME: strict validation of only that step + header.\nWith --pre-close: validate readiness before working-set collapse.\nWith --close-out: validate the collapsed ticket durable set.\n\npositional arguments:\n  analysis_dir          Path to the analysis directory (or the ticket directory for --pre-close/--close-out)\n\noptions:\n  -h, --help            show this help message and exit\n  --step {identify,investigate,synthesize}\n  --scaffold\n  --pre-close\n  --close-out\n  --repo-root REPO_ROOT\n\nExit code 0 = pass, 1 = fail, 2 = close-out skipped. Warnings do not affect the exit code.`);
} else {
  process.exitCode = runValidator(parsed.value);
}

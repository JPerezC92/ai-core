#!/usr/bin/env node
// Live-model classification eval for the ODD evidence profile. It answers a question the
// deterministic suite cannot: does a real message that asks for a repository change come back
// labelled `scope_changed: present`? The suite asserts contract shape, so a model returning one
// constant label would leave it green. Here the label is the assertion.
//
// It is not a unit test and must not be added to the Vitest suite or CI: every run depends on the
// local inference gateway. Each case is evaluated DEFAULT_RUNS times by default (`--runs N` changes
// that) and what is scored is the modal choice per label, its stability k/n and the mean confidence
// of the observations behind it, so a label that only sometimes lands right is visible instead of
// being averaged into agreement.
// The full probability map of every run is kept, not only its chosen state: a label whose state
// repeats while its scores move is reported as variable and fails the run, because agreement on the
// label alone cannot show a deterministic classifier. No sampling parameter is sent, so determinism
// is the gateway's property and can change with a model or LM Studio update.
// The set's coverage, the model pin and the confidence floor are all checked before or during the
// run, and each failure is reported with its literal reason. The result line states the run's own
// facts — it reports agreement on this run and never certifies the classifier.
//
// A case that names `imagePath` attaches that file as one inline image: it is read from the package
// root and sent as base64 bytes, so the path itself never reaches the model request. The case fails
// if the request its observation was built from carried zero inline images — the assertion is about
// the request payload, not about the file having been read — and the byte count is printed.
//
// The negative-control flag (`--negative-control`) inverts exactly one expectation for that run and
// shows that the harness reports a disagreement and exits 1. It never alters a default run.
//
// The server is spawned exactly as the plugin spawns it (`node <entry>`, package root as the
// working directory, the ambient environment plus the registered server's own defaults), so the
// transport, configuration and profile under test are the shipped ones. The model is never
// stubbed and nothing here imports src/: the boundary under test is the stdio tool, not a module.

import { readFile } from 'node:fs/promises';
import { isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';

// ---------------------------------------------------------------------------------------------
// Configuration. Paths resolve from this module, so the runner works from any working directory;
// the trailing separator a directory URL carries is removed so the working directory the child is
// handed and the path printed here are the same string.
// ---------------------------------------------------------------------------------------------

const PACKAGE_ROOT = fileURLToPath(new URL('..', import.meta.url)).replace(/[\\/]$/, '');
const SERVER_ENTRY = fileURLToPath(new URL('../src/mcp/stdio.ts', import.meta.url));
const CASE_FILE = fileURLToPath(new URL('./classification-cases.json', import.meta.url));

const NODE_COMMAND = 'node';
const TOOL_NAME = 'evaluate_odd_evidence';
const IMAGE_MIME_TYPE = 'image/png';

// The two label classes every scored question must exercise. Both are the profile's own choice
// vocabulary, not eval-local states.
const PRESENT = 'present';
const ABSENT = 'absent';

// The question this set exists for: a correct evaluation must land on `scope_changed: present` for
// a real change request, so one such case cannot outvote several negatives.
const SCOPE_CHANGED = 'scope_changed';
const MIN_SCOPE_CHANGED_PRESENT = 4;

// One sample cannot distinguish a classifier that lands on a label from one that occasionally does.
const DEFAULT_RUNS = 3;

// Below two runs there is nothing to compare, and above ten a set of this size cannot fit the
// shared deadline. A value outside the range is a usage error, never a silent clamp.
const MIN_RUNS = 2;
const MAX_RUNS = 10;
const RUNS_FLAG = '--runs';

// An agreed label whose mean confidence is below this is not agreement worth counting.
const CONFIDENCE_FLOOR = 0.6;

// The model this set was labelled against: the registered server default, compared with the
// resolved environment before any call and sent as the tool's `expectedModel`, so the server itself
// rejects an endpoint that answers with another model.
const EXPECTED_MODEL_ID = 'd1-2b@q8_0';

// The whole run is bounded, not each call: cases × runs share this budget, so a gateway that stops
// answering fails the run at the deadline instead of hanging it.
const DEADLINE_MS = 600_000;

// Defaults the registered server is given in `opencode.jsonc` (`mcp.servers.system-one`). They fill
// only an unset or blank variable, so an ambient override still wins — and the model pin fails the
// run rather than silently scoring a different model.
const CONFIGURED_DEFAULTS: Readonly<Record<string, string>> = {
  SYSTEM_ONE_ENDPOINT: 'http://127.0.0.1:1234',
  SYSTEM_ONE_MODEL: EXPECTED_MODEL_ID,
  SYSTEM_ONE_TIMEOUT_MS: '15000',
};

// The reported state for a question the evaluation did not answer at all. It is not a profile
// state and is never compared as one; it marks a missing answer as the disagreement it is.
const MISSING = '(missing)';
const UNSET = '(unset)';
const NO_CONFIDENCE = '(none)';
const NO_PROBABILITY = '(none)';
const CLOSE_GRACE_MS = 5_000;
const NEGATIVE_CONTROL_FLAG = '--negative-control';
const MAX_REASON_LENGTH = 500;

// ---------------------------------------------------------------------------------------------
// Domain: records, port contracts and typed results. No IO, no transport types.
// ---------------------------------------------------------------------------------------------

type Predicate = {
  readonly question: string;
  readonly source: string;
  readonly statement: string;
};

type ExpectedProfile = {
  readonly profileId: string;
  readonly version: number;
};

type ClassificationCase = {
  readonly id: string;
  readonly text: string;
  readonly expected: Readonly<Record<string, string>>;
  readonly note: string;
  // Package-root-relative path of the one inline image the case supplies, when it supplies one.
  readonly imagePath?: string;
};

type ClassificationCaseSet = {
  readonly description: string;
  readonly predicate: Predicate;
  readonly profile: ExpectedProfile;
  readonly cases: ReadonlyArray<ClassificationCase>;
};

// One answer's score per evidence state, as the gateway returned it. It is kept whole because a
// determinism claim is about every state, not only the one that was chosen.
type ProbabilityMap = Readonly<Record<string, number>>;

type AnswerRecord = {
  readonly choice: string;
  readonly confidence?: number;
  // Absent when the payload carried no usable score map; the label's determinism is then unknown.
  readonly probabilities?: ProbabilityMap;
};

// One evaluation as it came back from the tool: the profile it was scored under, the answers, and
// the image payload the request that produced it actually carried.
type Observation = {
  readonly profileId: string;
  readonly profileVersion: number;
  readonly answers: Readonly<Record<string, AnswerRecord>>;
  readonly imagesSent: number;
  readonly imageBytes: number;
};

type EvidenceRequest = {
  readonly caseId: string;
  readonly text: string;
  readonly imagePath?: string;
};

// The declared outcome of one tool call: either an evaluation or a literal reason it could not be
// obtained. The adapter classifies unavailability; the operation decides what it means for a case.
type EvidenceOutcome =
  | { readonly kind: 'evaluated'; readonly observation: Observation }
  | { readonly kind: 'failed'; readonly reason: string };

// Port: evaluate one message once. Implementations perform the IO; the shape is domain-owned.
type EvidenceEvaluator = {
  evaluate(request: EvidenceRequest): Promise<EvidenceOutcome>;
};

// Port: the labelled case set. The adapter owns file IO and the mapping step.
type ClassificationCaseSource = {
  load(): Promise<ClassificationCaseSet>;
};

type ScoringParameters = {
  readonly runs: number;
  readonly confidenceFloor: number;
};

// Whether the whole probability map, not just the chosen state, was identical on every run:
// `maps` counts the runs that carried a comparable map (fewer than `runs` means the property could
// not be established), `distinct` counts the different maps observed, and the two probabilities
// are the range the modal state's own value covered.
type Determinism = {
  readonly maps: number;
  readonly runs: number;
  readonly distinct: number;
  readonly modalState: string;
  readonly minProbability?: number;
  readonly maxProbability?: number;
};

// One scored label: the modal choice over its runs, how stable that modal was, the mean
// confidence of the observations that chose it, and whether its probability maps were identical.
type LabelScore = {
  readonly caseId: string;
  readonly question: string;
  readonly expected: string;
  readonly modal: string;
  readonly stability: number;
  readonly runs: number;
  readonly confidence?: number;
  readonly confidenceSamples: number;
  readonly lowConfidence: boolean;
  readonly determinism: Determinism;
};

// What one observation of an image case placed in its request, reported so the record can state it.
type ImageSend = {
  readonly caseId: string;
  readonly run: number;
  readonly source: string;
  readonly imagesSent: number;
  readonly bytes: number;
};

// One question of one run. `expected` is undefined for a question the case does not score.
type Comparison = {
  readonly id: string;
  readonly question: string;
  readonly expected: string | undefined;
  readonly got: string;
};

type UnscoredRow = {
  readonly question: string;
  readonly choice: string;
  readonly count: number;
};

type ConfusionRow = {
  readonly question: string;
  readonly expected: string;
  readonly got: string;
  readonly count: number;
};

type CoverageCounts = {
  readonly question: string;
  readonly present: number;
  readonly absent: number;
  readonly other: ReadonlyArray<string>;
};

type Coverage = {
  readonly counts: ReadonlyArray<CoverageCounts>;
  readonly lines: ReadonlyArray<string>;
  readonly failures: ReadonlyArray<string>;
};

type ClassificationScore = {
  readonly cases: number;
  readonly casesEvaluated: number;
  readonly runs: number;
  readonly observations: number;
  readonly labels: ReadonlyArray<LabelScore>;
  readonly comparisons: ReadonlyArray<Comparison>;
  readonly imageSends: ReadonlyArray<ImageSend>;
  readonly profiles: ReadonlyArray<string>;
  readonly failures: ReadonlyArray<string>;
};

type Inversion = {
  readonly caseId: string;
  readonly question: string;
  readonly from: string;
  readonly to: string;
};

// ---------------------------------------------------------------------------------------------
// Domain: pure rules. Coverage, modal choice, label summarising, confusion. No IO, no policy about
// the model beyond what the parameters state.
// ---------------------------------------------------------------------------------------------

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function describeError(error: unknown): string {
  return error instanceof Error ? `${error.name}: ${error.message}` : String(error);
}

function boundReason(text: string): string {
  return text.length > MAX_REASON_LENGTH ? text.slice(0, MAX_REASON_LENGTH) : text;
}

// The most frequent choice over the runs, with the first-encountered choice winning a tie so the
// result is deterministic. A tied modal is itself evidence of instability, which `stability` reports.
function modeOf(choices: ReadonlyArray<string>): { readonly choice: string; readonly stability: number } {
  const counts = new Map<string, number>();
  for (const choice of choices) counts.set(choice, (counts.get(choice) ?? 0) + 1);

  let choice = MISSING;
  let stability = 0;
  for (const [candidate, count] of counts) {
    if (count > stability) {
      choice = candidate;
      stability = count;
    }
  }
  return { choice, stability };
}

// Key order is not part of a probability distribution, so a map is reduced to its sorted
// state=value pairs: two maps are identical exactly when their identities are equal.
function probabilityMapIdentity(probabilities: ProbabilityMap): string {
  return Object.entries(probabilities)
    .sort(([left], [right]) => (left < right ? -1 : left > right ? 1 : 0))
    .map(([state, value]) => `${state}=${value}`)
    .join('\u0000');
}

// Determinism is a property of the whole map, not of the chosen state, so a run whose score map is
// missing cannot be compared and leaves the label's determinism unestablished rather than assumed.
function assessDeterminism(
  answers: ReadonlyArray<AnswerRecord | undefined>,
  modalState: string,
  runs: number,
): Determinism {
  const maps: Array<ProbabilityMap> = [];
  for (const answer of answers) {
    if (answer?.probabilities === undefined) continue;
    maps.push(answer.probabilities);
  }

  const modalValues: Array<number> = [];
  for (const map of maps) {
    const value = map[modalState];
    if (value !== undefined) modalValues.push(value);
  }

  return {
    maps: maps.length,
    runs,
    distinct: new Set(maps.map(probabilityMapIdentity)).size,
    modalState,
    ...(modalValues.length === 0
      ? {}
      : { minProbability: Math.min(...modalValues), maxProbability: Math.max(...modalValues) }),
  };
}

// The modal state's own observed range, so a variable label can be read without re-running it.
function probabilityRange(determinism: Determinism): string {
  return determinism.minProbability === undefined || determinism.maxProbability === undefined
    ? NO_PROBABILITY
    : `${determinism.minProbability}-${determinism.maxProbability}`;
}

function summariseLabel(
  caseId: string,
  question: string,
  expected: string,
  answers: ReadonlyArray<AnswerRecord | undefined>,
  runs: number,
  confidenceFloor: number,
): LabelScore {
  const { choice: modal, stability } = modeOf(answers.map((answer) => answer?.choice ?? MISSING));

  const confidences: Array<number> = [];
  for (const answer of answers) {
    if (answer === undefined) continue;
    if (answer.choice !== modal) continue;
    if (answer.confidence === undefined) continue;
    confidences.push(answer.confidence);
  }
  const mean = confidences.length === 0
    ? undefined
    : confidences.reduce((total, value) => total + value, 0) / confidences.length;

  return {
    caseId,
    question,
    expected,
    modal,
    stability,
    runs,
    ...(mean === undefined ? {} : { confidence: mean }),
    confidenceSamples: confidences.length,
    // Only an agreed label can be low-confidence agreement; a disagreement is already a failure.
    lowConfidence: modal === expected && mean !== undefined && mean < confidenceFloor,
    determinism: assessDeterminism(answers, modal, runs),
  };
}

// Coverage is a property of the set, not of a run. A question scored with only one label cannot
// tell a correct evaluation from a constant-label model, so the set is defective before the model
// is asked; the failure is reported with the question and the counts that produced it.
function assessCoverage(cases: ReadonlyArray<ClassificationCase>): Coverage {
  const perQuestion = new Map<string, { present: number; absent: number; other: Set<string> }>();
  for (const caseValue of cases) {
    for (const [question, expected] of Object.entries(caseValue.expected)) {
      const current = perQuestion.get(question) ?? { present: 0, absent: 0, other: new Set<string>() };
      if (expected === PRESENT) current.present += 1;
      else if (expected === ABSENT) current.absent += 1;
      else current.other.add(expected);
      perQuestion.set(question, current);
    }
  }

  const counts: ReadonlyArray<CoverageCounts> = [...perQuestion.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([question, current]) => ({
      question,
      present: current.present,
      absent: current.absent,
      other: [...current.other].sort(),
    }));

  const failures: Array<string> = [];
  if (counts.length === 0) failures.push('coverage · the set scores no question at all');
  for (const count of counts) {
    for (const label of count.other) {
      failures.push(
        `coverage · ${count.question} · expected label "${label}" is neither ${PRESENT} nor ${ABSENT}`,
      );
    }
    if (count.present === 0) {
      failures.push(
        `coverage · ${count.question} · 0 expected ${PRESENT} cases; at least one ${PRESENT} and one ${ABSENT} case are required`,
      );
    }
    if (count.absent === 0) {
      failures.push(
        `coverage · ${count.question} · 0 expected ${ABSENT} cases; at least one ${PRESENT} and one ${ABSENT} case are required`,
      );
    }
  }
  const scopeChangedPresent = counts.find((count) => count.question === SCOPE_CHANGED)?.present ?? 0;
  if (scopeChangedPresent < MIN_SCOPE_CHANGED_PRESENT) {
    const caseWord = scopeChangedPresent === 1 ? 'case' : 'cases';
    failures.push(
      `coverage · ${SCOPE_CHANGED} · ${scopeChangedPresent} expected ${PRESENT} ${caseWord}; at least ${MIN_SCOPE_CHANGED_PRESENT} are required`,
    );
  }

  return {
    counts,
    lines: counts.map(
      (count) =>
        `coverage · ${count.question} · expected ${PRESENT}: ${count.present} · expected ${ABSENT}: ${count.absent}`,
    ),
    failures,
  };
}

// Expected × got over every scored run, including the zero cells: a missing cell hides a label that
// was never exercised, which is exactly the gap this eval exists to expose.
function buildConfusion(comparisons: ReadonlyArray<Comparison>): ReadonlyArray<ConfusionRow> {
  const perQuestion = new Map<string, Array<Comparison>>();
  for (const comparison of comparisons) {
    if (comparison.expected === undefined) continue;
    const current = perQuestion.get(comparison.question) ?? [];
    current.push(comparison);
    perQuestion.set(comparison.question, current);
  }

  const rows: Array<ConfusionRow> = [];
  const questions = [...perQuestion.entries()].sort(([left], [right]) => left.localeCompare(right));
  for (const [question, entries] of questions) {
    const expectedStates = [...new Set(entries.map((entry) => entry.expected ?? MISSING))].sort();
    const gotStates = [...new Set([...entries.map((entry) => entry.got), ...expectedStates])].sort();
    for (const expected of expectedStates) {
      for (const got of gotStates) {
        rows.push({
          question,
          expected,
          got,
          count: entries.filter((entry) => entry.expected === expected && entry.got === got).length,
        });
      }
    }
  }
  return rows;
}

// The questions a case does not score are still printed, in aggregate, so the record shows what
// the evaluation returned without asserting anything about it.
function buildUnscored(comparisons: ReadonlyArray<Comparison>): ReadonlyArray<UnscoredRow> {
  const perQuestion = new Map<string, Map<string, number>>();
  for (const comparison of comparisons) {
    if (comparison.expected !== undefined) continue;
    const perChoice = perQuestion.get(comparison.question) ?? new Map<string, number>();
    perChoice.set(comparison.got, (perChoice.get(comparison.got) ?? 0) + 1);
    perQuestion.set(comparison.question, perChoice);
  }
  return [...perQuestion.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .flatMap(([question, perChoice]) =>
      [...perChoice.entries()]
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([choice, count]) => ({ question, choice, count })),
    );
}

// ---------------------------------------------------------------------------------------------
// Case-file mapping. A malformed case file is a defect in the eval, not a model result, so it fails
// loudly with the field that is wrong rather than scoring nothing and reporting agreement.
// ---------------------------------------------------------------------------------------------

function parseCaseSet(value: unknown): ClassificationCaseSet {
  if (!isRecord(value)) throw new Error('case file: the top level must be an object');

  const predicate = parsePredicate(value.predicate);

  const profile = value.profile;
  if (!isRecord(profile)) throw new Error('case file: "profile" must be an object');
  const profileId = profile.profileId;
  const version = profile.version;
  if (typeof profileId !== 'string' || profileId.length === 0) {
    throw new Error('case file: "profile.profileId" must be a non-empty string');
  }
  if (typeof version !== 'number' || !Number.isInteger(version) || version <= 0) {
    throw new Error('case file: "profile.version" must be a positive integer');
  }

  const rawCases = value.cases;
  if (!Array.isArray(rawCases) || rawCases.length === 0) {
    throw new Error('case file: "cases" must be a non-empty array');
  }

  const cases = rawCases.map((rawCase, index) => parseCase(rawCase, index));
  const ids = new Set(cases.map((entry) => entry.id));
  if (ids.size !== cases.length) throw new Error('case file: case ids must be unique');

  return {
    description: typeof value.description === 'string' ? value.description : '',
    predicate,
    profile: { profileId, version },
    cases,
  };
}

// The set states one predicate, quoted from the profile it scores, and every note has to cite it.
// A set without it has no adjudicable label, so its absence is a file defect.
function parsePredicate(value: unknown): Predicate {
  if (!isRecord(value)) throw new Error('case file: "predicate" must state the one predicate this set scores');

  const question = value.question;
  const source = value.source;
  const statement = value.statement;
  if (typeof question !== 'string' || question.trim().length === 0) {
    throw new Error('case file: "predicate.question" must be a non-empty string');
  }
  if (typeof source !== 'string' || source.trim().length === 0) {
    throw new Error('case file: "predicate.source" must name where the sentence is written');
  }
  // A paraphrase cannot be checked against its owner, so the statement must not be a summary.
  if (typeof statement !== 'string' || statement.trim().length === 0) {
    throw new Error('case file: "predicate.statement" must be the quoted predicate');
  }

  return { question, source, statement };
}

function parseCase(value: unknown, index: number): ClassificationCase {
  const label = `case file: cases[${index}]`;
  if (!isRecord(value)) throw new Error(`${label} must be an object`);

  const id = value.id;
  if (typeof id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(id)) {
    throw new Error(`${label}.id must be 1-64 characters of [A-Za-z0-9_-]`);
  }

  const text = value.text;
  if (typeof text !== 'string' || text.trim().length === 0) {
    throw new Error(`${label}.text must be a non-empty string`);
  }

  // The note is what makes the label contestable, so an unstated label is a file defect.
  const note = value.note;
  if (typeof note !== 'string' || note.trim().length === 0) {
    throw new Error(`${label}.note must state why the label is right`);
  }

  const rawExpected = value.expected;
  if (!isRecord(rawExpected)) throw new Error(`${label}.expected must be an object of question → label`);
  const expected: Record<string, string> = {};
  for (const [question, choice] of Object.entries(rawExpected)) {
    if (!/^[a-z][a-z0-9_]*$/.test(question)) {
      throw new Error(`${label}.expected has an invalid question id "${question}"`);
    }
    if (typeof choice !== 'string' || choice.length === 0) {
      throw new Error(`${label}.expected.${question} must be a non-empty string`);
    }
    expected[question] = choice;
  }
  if (Object.keys(expected).length === 0) {
    throw new Error(`${label}.expected must name at least one question`);
  }

  // `undecided` states the questions a case's text cannot decide, and the set's own description
  // says such a question is left out of `expected`. Nothing else reads the array, so without this
  // check a case that listed a question in both places would be scored as though it had decided
  // it; the contradiction is a case-file defect and is reported with the case and the question.
  const undecided = value.undecided;
  if (undecided !== undefined) {
    if (!Array.isArray(undecided)) {
      throw new Error(`${label}.undecided must be an array when present`);
    }
    for (const entry of undecided) {
      if (!isRecord(entry) || typeof entry.question !== 'string' || entry.question.length === 0) {
        throw new Error(`${label}.undecided entries must be objects with a non-empty "question"`);
      }
      if (expected[entry.question] !== undefined) {
        throw new Error(
          `${label} · ${id} · "${entry.question}" is listed in both "undecided" and "expected"; a question is either undecided or scored, never both`,
        );
      }
    }
  }

  // A case may attach one inline image, named by a package-root-relative path. An absolute path or
  // one that climbs out of the package would read an unassigned file, so both are file defects.
  const imagePath = value.imagePath;
  if (imagePath !== undefined) {
    if (typeof imagePath !== 'string' || imagePath.trim().length === 0) {
      throw new Error(`${label}.imagePath must be a non-empty string when present`);
    }
    if (isAbsolute(imagePath) || imagePath.split(/[\\/]/).includes('..')) {
      throw new Error(`${label}.imagePath must be relative to the package root and stay inside it`);
    }
  }

  return {
    id,
    text,
    expected,
    note,
    ...(typeof imagePath === 'string' ? { imagePath } : {}),
  };
}

// The negative control: flip exactly one scored expectation for that run and nothing else, so a
// reported disagreement can only come from the flipped label.
function invertOneExpectation(
  caseSet: ClassificationCaseSet,
): { readonly caseSet: ClassificationCaseSet; readonly inversion: Inversion } {
  for (const [index, caseValue] of caseSet.cases.entries()) {
    for (const [question, expected] of Object.entries(caseValue.expected)) {
      const inverted = expected === PRESENT ? ABSENT : expected === ABSENT ? PRESENT : undefined;
      if (inverted === undefined) continue;

      const cases = caseSet.cases.map((entry, entryIndex) =>
        entryIndex === index
          ? { ...entry, expected: { ...entry.expected, [question]: inverted } }
          : entry,
      );
      return {
        caseSet: { ...caseSet, cases },
        inversion: { caseId: caseValue.id, question, from: expected, to: inverted },
      };
    }
  }
  throw new Error(`case file: no scored ${PRESENT}/${ABSENT} expectation to invert for the negative control`);
}

// ---------------------------------------------------------------------------------------------
// Infrastructure adapters: IO, external payload mapping, no business rules.
// ---------------------------------------------------------------------------------------------

// The child's environment: the ambient one, with the registered server's defaults filling only what
// the ambient environment leaves unset or blank.
function buildChildEnvironment(ambient: NodeJS.ProcessEnv): Record<string, string> {
  const environment: Record<string, string> = {};
  for (const [name, value] of Object.entries(ambient)) {
    if (value === undefined) continue;
    environment[name] = value;
  }
  for (const [name, fallback] of Object.entries(CONFIGURED_DEFAULTS)) {
    const current = environment[name]?.trim();
    if (current === undefined || current.length === 0) environment[name] = fallback;
  }
  return environment;
}

class JsonCaseFileSource implements ClassificationCaseSource {
  readonly #path: string;

  constructor(options: { readonly path: string }) {
    this.#path = options.path;
  }

  async load(): Promise<ClassificationCaseSet> {
    return parseCaseSet(JSON.parse(await readFile(this.#path, 'utf8')));
  }
}

type InlineImage = {
  readonly mimeType: string;
  readonly base64: string;
};

type McpEvidenceEvaluatorOptions = {
  readonly client: Client;
  readonly expectedModel: string;
  readonly startedAt: number;
  readonly deadlineMs: number;
  readonly deadline: Promise<never>;
};

// One tool call per evaluation: the image bytes of the case, if it declares one, and the shared
// run deadline. A transport failure, a rejection and an exceeded deadline are each reported with
// their literal reason instead of being retried into a plausible result.
class McpEvidenceEvaluator implements EvidenceEvaluator {
  readonly #client: Client;
  readonly #expectedModel: string;
  readonly #startedAt: number;
  readonly #deadlineMs: number;
  readonly #deadline: Promise<never>;

  constructor(options: McpEvidenceEvaluatorOptions) {
    this.#client = options.client;
    this.#expectedModel = options.expectedModel;
    this.#startedAt = options.startedAt;
    this.#deadlineMs = options.deadlineMs;
    this.#deadline = options.deadline;
  }

  async evaluate(request: EvidenceRequest): Promise<EvidenceOutcome> {
    const images: Array<InlineImage> = [];
    let imageBytes = 0;

    if (request.imagePath !== undefined) {
      try {
        const bytes = await readFile(resolve(PACKAGE_ROOT, request.imagePath));
        imageBytes = bytes.byteLength;
        images.push({ mimeType: IMAGE_MIME_TYPE, base64: bytes.toString('base64') });
      } catch (error) {
        return { kind: 'failed', reason: `image · ${request.imagePath} · ${describeError(error)}` };
      }
    }

    // The request payload is built once, and the record reports the `images` array of that same
    // object: the assertion is about what the request carried, not about the file having been read.
    const argumentsPayload = {
      text: request.text,
      images,
      expectedModel: this.#expectedModel,
    };
    const remainingMs = Math.max(1, this.#deadlineMs - (Date.now() - this.#startedAt));

    try {
      const result = await Promise.race([
        this.#client.callTool(
          { name: TOOL_NAME, arguments: argumentsPayload },
          { timeout: remainingMs },
        ),
        this.#deadline,
      ]);
      return readObservation(result, argumentsPayload.images.length, imageBytes);
    } catch (error) {
      return { kind: 'failed', reason: `transport · ${describeError(error)}` };
    }
  }
}

function readResultText(content: unknown): string | undefined {
  if (!Array.isArray(content)) return undefined;
  for (const entry of content) {
    if (!isRecord(entry) || entry.type !== 'text' || typeof entry.text !== 'string') continue;
    return entry.text;
  }
  return undefined;
}

function readTextPayload(content: unknown): Record<string, unknown> | undefined {
  if (!Array.isArray(content)) return undefined;
  for (const entry of content) {
    if (!isRecord(entry) || entry.type !== 'text' || typeof entry.text !== 'string') continue;
    try {
      const parsed: unknown = JSON.parse(entry.text);
      if (isRecord(parsed)) return parsed;
    } catch {
      // A text block that is not JSON is not the payload; keep looking.
    }
  }
  return undefined;
}

// The gateway's own score per state is part of the answer, not decoration: the determinism check
// compares the whole map, so it is kept even though the chosen state alone would score the label.
// A payload with no numeric entry yields no map, and the label then reports determinism as unknown.
function readProbabilities(value: unknown): ProbabilityMap | undefined {
  if (!isRecord(value)) return undefined;

  const probabilities: Record<string, number> = {};
  for (const [state, probability] of Object.entries(value)) {
    if (typeof probability === 'number') probabilities[state] = probability;
  }
  return Object.keys(probabilities).length === 0 ? undefined : probabilities;
}

function readAnswers(value: Readonly<Record<string, unknown>>): Readonly<Record<string, AnswerRecord>> {
  const answers: Record<string, AnswerRecord> = {};
  for (const [question, raw] of Object.entries(value)) {
    if (!isRecord(raw)) continue;
    const choice = raw.choice;
    if (typeof choice !== 'string' || choice.length === 0) continue;
    const confidence = raw.confidence;
    const probabilities = readProbabilities(raw.probabilities);
    answers[question] = {
      choice,
      ...(typeof confidence === 'number' ? { confidence } : {}),
      ...(probabilities === undefined ? {} : { probabilities }),
    };
  }
  return answers;
}

// The tool payload is mapped to the observation this module scores. The success branch is the
// evaluation; anything else is a bounded non-evaluated outcome whose literal reason is reported.
function readObservation(result: unknown, imagesSent: number, imageBytes: number): EvidenceOutcome {
  if (!isRecord(result)) {
    return { kind: 'failed', reason: 'payload carried no structured or text evaluation' };
  }

  // An error result fails the case whatever its payload says: a payload shaped like a success is
  // not evidence that the call succeeded, so `isError` is read before the payload is.
  if (result.isError === true) {
    const text = readResultText(result.content);
    const detail = text === undefined ? 'no error text' : boundReason(text);
    return { kind: 'failed', reason: `outcome · isError (${detail})` };
  }

  const payload = isRecord(result.structuredContent) ? result.structuredContent : readTextPayload(result.content);
  if (payload === undefined) {
    return { kind: 'failed', reason: 'payload carried no structured or text evaluation' };
  }

  if (payload.ok !== true) {
    const code = typeof payload.code === 'string' ? payload.code : '(no code)';
    const reason = typeof payload.reason === 'string' ? payload.reason : '(no reason)';
    return { kind: 'failed', reason: `rejected ${code}: ${reason}` };
  }

  const profileId = payload.profileId;
  const profileVersion = payload.profileVersion;
  const answers = payload.answers;
  if (typeof profileId !== 'string' || typeof profileVersion !== 'number' || !isRecord(answers)) {
    return {
      kind: 'failed',
      reason: 'success payload is missing profileId, profileVersion or answers',
    };
  }

  return {
    kind: 'evaluated',
    observation: {
      profileId,
      profileVersion,
      answers: readAnswers(answers),
      imagesSent,
      imageBytes,
    },
  };
}

// ---------------------------------------------------------------------------------------------
// Application operation: score a classified set. It owns the run policy — repeats, modal/stability,
// the confidence floor, the image assertion, the profile assertion — and the scoring consequences
// of an unavailable evaluation. It performs no IO of its own; every effect goes through the ports.
// ---------------------------------------------------------------------------------------------

type ScoreClassificationSetDependencies = {
  readonly evidenceEvaluator: EvidenceEvaluator;
};

class ScoreClassificationSet {
  readonly #evidenceEvaluator: EvidenceEvaluator;

  constructor(dependencies: ScoreClassificationSetDependencies) {
    this.#evidenceEvaluator = dependencies.evidenceEvaluator;
  }

  async execute(
    caseSet: ClassificationCaseSet,
    parameters: ScoringParameters,
  ): Promise<ClassificationScore> {
    const failures: Array<string> = [];
    const labels: Array<LabelScore> = [];
    const comparisons: Array<Comparison> = [];
    const imageSends: Array<ImageSend> = [];
    const profiles = new Set<string>();
    let observations = 0;
    let casesEvaluated = 0;

    for (const caseValue of caseSet.cases) {
      const perQuestion = new Map<string, Array<AnswerRecord | undefined>>();
      for (const question of Object.keys(caseValue.expected)) perQuestion.set(question, []);
      let caseObservations = 0;

      for (let run = 1; run <= parameters.runs; run += 1) {
        const request: EvidenceRequest = {
          caseId: caseValue.id,
          text: caseValue.text,
          ...(caseValue.imagePath === undefined ? {} : { imagePath: caseValue.imagePath }),
        };
        const outcome = await this.#evidenceEvaluator.evaluate(request);

        if (outcome.kind === 'failed') {
          failures.push(`${caseValue.id} · run ${run} · ${outcome.reason}`);
          for (const answers of perQuestion.values()) answers.push(undefined);
          continue;
        }

        const observation = outcome.observation;
        caseObservations += 1;
        observations += 1;
        profiles.add(`${observation.profileId} v${observation.profileVersion}`);

        // The image assertion: a case that declares an image must have carried at least one in the
        // request it was evaluated from, and a case that declares none must carry none.
        if (caseValue.imagePath !== undefined) {
          imageSends.push({
            caseId: caseValue.id,
            run,
            source: caseValue.imagePath,
            imagesSent: observation.imagesSent,
            bytes: observation.imageBytes,
          });
          if (observation.imagesSent === 0) {
            failures.push(
              `${caseValue.id} · run ${run} · image · the case declares ${caseValue.imagePath} but its request carried 0 inline images`,
            );
          }
        } else if (observation.imagesSent !== 0) {
          failures.push(
            `${caseValue.id} · run ${run} · image · the case declares no image but its request carried ${observation.imagesSent} inline image(s)`,
          );
        }

        for (const [question, answers] of perQuestion) {
          answers.push(observation.answers[question]);
        }

        const questions = new Set([
          ...Object.keys(observation.answers),
          ...Object.keys(caseValue.expected),
        ]);
        for (const question of questions) {
          comparisons.push({
            id: caseValue.id,
            question,
            expected: caseValue.expected[question],
            got: observation.answers[question]?.choice ?? MISSING,
          });
        }
      }

      if (caseObservations > 0) casesEvaluated += 1;

      for (const [question, answers] of perQuestion) {
        const expected = caseValue.expected[question];
        if (expected === undefined) continue;

        const label = summariseLabel(
          caseValue.id,
          question,
          expected,
          answers,
          parameters.runs,
          parameters.confidenceFloor,
        );
        labels.push(label);

        if (label.modal !== expected) {
          // The modal mismatch line already states the k/n it was reached with, so a separate
          // instability reason would report the same observations twice.
          failures.push(
            `${label.caseId} · ${label.question} · expected ${expected} → modal ${label.modal} (agreement ${label.stability}/${label.runs})`,
          );
        } else if (label.stability < label.runs) {
          failures.push(
            `${label.caseId} · ${label.question} · label changed between runs: agreement ${label.stability}/${label.runs}`,
          );
        }
        if (label.lowConfidence) {
          failures.push(
            `${label.caseId} · ${label.question} · low confidence ${label.confidence?.toFixed(2) ?? NO_CONFIDENCE} < ${parameters.confidenceFloor} for modal ${label.modal}`,
          );
        }
        if (label.determinism.maps < label.determinism.runs) {
          failures.push(
            `${label.caseId} · ${label.question} · determinism: only ${label.determinism.maps} of ${label.determinism.runs} runs carried a probability map, so determinism cannot be established`,
          );
        } else if (label.determinism.distinct > 1) {
          // A repeated choice is not determinism: the gateway can land on the same state while its
          // scores move, which is exactly what a label-only comparison hides.
          failures.push(
            `${label.caseId} · ${label.question} · determinism: ${label.determinism.distinct} distinct probability maps over ${label.determinism.runs} runs (${label.determinism.modalState} ${probabilityRange(label.determinism)}); the chosen state repeats but its probabilities move, so this run is not deterministic`,
          );
        }
      }
    }

    // The labels are this profile's labels. Scoring them against another profile would report
    // agreement that proves nothing about the profile this set belongs to.
    const observed = [...profiles].sort();
    const expectedProfile = `${caseSet.profile.profileId} v${caseSet.profile.version}`;
    if (observed.length !== 1 || observed[0] !== expectedProfile) {
      failures.push(
        `profile · expected ${expectedProfile} → got ${observed.length === 0 ? '(no successful evaluation)' : observed.join(' | ')}`,
      );
    }

    return {
      cases: caseSet.cases.length,
      casesEvaluated,
      runs: parameters.runs,
      observations,
      labels,
      comparisons,
      imageSends,
      profiles: observed,
      failures,
    };
  }
}

// ---------------------------------------------------------------------------------------------
// Delivery: command line, rendering and the composition root. No scoring rule lives here.
// ---------------------------------------------------------------------------------------------

type CommandLine = {
  readonly negativeControl: boolean;
  readonly runs: number;
};

// The run count is a usage decision, so an out-of-range or non-integer value is reported literally
// rather than clamped: a silently clamped run count would misstate how many samples were scored.
function parseRuns(value: string | undefined): number {
  const range = `an integer from ${MIN_RUNS} to ${MAX_RUNS}`;
  if (value === undefined) {
    throw new Error(`${RUNS_FLAG} must be ${range}; the flag was given no value`);
  }
  if (!/^[0-9]+$/.test(value)) {
    throw new Error(`${RUNS_FLAG} must be ${range}; got "${value}"`);
  }
  const runs = Number(value);
  if (runs < MIN_RUNS || runs > MAX_RUNS) {
    throw new Error(`${RUNS_FLAG} must be ${range}; got "${value}"`);
  }
  return runs;
}

function readCommandLine(argv: ReadonlyArray<string>): CommandLine {
  let negativeControl = false;
  let runs = DEFAULT_RUNS;

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === NEGATIVE_CONTROL_FLAG) {
      negativeControl = true;
      continue;
    }
    if (argument === RUNS_FLAG) {
      runs = parseRuns(argv[index + 1]);
      index += 1;
      continue;
    }
    // An unrecognised flag is a mistake, not a request to run the default set: a typo in the
    // control flag would otherwise silently look like a control that ran.
    throw new Error(
      `unrecognised argument "${argument}"; supported flags are ${NEGATIVE_CONTROL_FLAG} and ${RUNS_FLAG} N`,
    );
  }
  return { negativeControl, runs };
}

function displayPath(absolutePath: string): string {
  const relativePath = relative(process.cwd(), absolutePath);
  return relativePath.length === 0 || relativePath.startsWith('..') ? absolutePath : relativePath;
}

function renderImageSend(sends: ReadonlyArray<ImageSend>): string {
  const first = sends[0];
  if (first === undefined) return '';
  return `image · ${first.caseId} · ${first.source} · ${first.bytes} bytes · ${IMAGE_MIME_TYPE} inline · ${first.imagesSent} image per request · observed on ${sends.length} run${sends.length === 1 ? '' : 's'}`;
}

// One label line states whether the whole probability map was identical on every run. A label
// cannot be called deterministic when a run carried no map: that is reported, not assumed.
function renderDeterminism(determinism: Determinism): string {
  if (determinism.maps < determinism.runs) {
    return `determinism undetermined · ${determinism.maps}/${determinism.runs} runs carried a probability map`;
  }
  if (determinism.distinct <= 1) {
    return `determinism deterministic · 1 distinct map · ${determinism.maps}/${determinism.runs} runs`;
  }
  return `determinism variable · ${determinism.distinct} distinct maps · ${determinism.modalState} ${probabilityRange(determinism)}`;
}

function renderLabel(label: LabelScore): string {
  const confidence = label.confidence === undefined
    ? `${NO_CONFIDENCE} of ${label.runs}`
    : `${label.confidence.toFixed(2)} over ${label.confidenceSamples}/${label.runs}`;
  return `${label.caseId} · ${label.question} · expected ${label.expected} → modal ${label.modal} · agreement ${label.stability}/${label.runs} · confidence ${confidence} · ${renderDeterminism(label.determinism)}${label.lowConfidence ? ' · LOW CONFIDENCE' : ''}`;
}

function renderCaseResults(score: ClassificationScore): ReadonlyArray<string> {
  const lines: Array<string> = [];
  const printedCases = new Set<string>();
  for (const label of score.labels) {
    if (!printedCases.has(label.caseId)) {
      printedCases.add(label.caseId);
      const sends = score.imageSends.filter((send) => send.caseId === label.caseId);
      if (sends.length > 0) lines.push(renderImageSend(sends));
    }
    lines.push(renderLabel(label));
  }
  return lines;
}

async function closeQuietly(client: Client): Promise<void> {
  // Bounded teardown: a wedged child must not keep the run alive after the deadline.
  await Promise.race([
    client.close().catch(() => undefined),
    new Promise<void>((done) => {
      setTimeout(done, CLOSE_GRACE_MS);
    }),
  ]);
}

async function main(): Promise<number> {
  const startedAt = Date.now();
  const commandLine = readCommandLine(process.argv.slice(2));
  const caseSet = await new JsonCaseFileSource({ path: CASE_FILE }).load();
  const coverage = assessCoverage(caseSet.cases);
  const environment = buildChildEnvironment(process.env);
  const resolvedModel = environment.SYSTEM_ONE_MODEL ?? UNSET;
  const expectedProfile = `${caseSet.profile.profileId} v${caseSet.profile.version}`;

  const header = [
    'system-one classification eval — live model, not part of the deterministic suite',
    `cases: ${displayPath(CASE_FILE)} (${caseSet.cases.length}) · runs per case: ${commandLine.runs} (${RUNS_FLAG} N, ${MIN_RUNS} to ${MAX_RUNS}; default ${DEFAULT_RUNS}) · deadline: ${DEADLINE_MS} ms`,
    `predicate (${caseSet.predicate.source}): ${caseSet.predicate.statement}`,
    `server: ${NODE_COMMAND} ${displayPath(SERVER_ENTRY)} (cwd=${displayPath(PACKAGE_ROOT)})`,
    `model: ${resolvedModel} (pinned ${EXPECTED_MODEL_ID}) · endpoint: ${environment.SYSTEM_ONE_ENDPOINT ?? UNSET}`,
    `expects profile: ${expectedProfile}`,
    `confidence floor: ${CONFIDENCE_FLOOR} for an agreed label; confidence is the mean over the observations that chose the modal label`,
    'determinism: no sampling parameter is sent — the request body is model, state and questions only, plus images when present, with no temperature, seed or top_p — so identical probabilities across runs are the gateway\'s property, not this code\'s, and can change with a model or LM Studio update; any label whose full probability map differs between runs is reported variable and fails the run',
    'limitations: when a payload carries no confidence the floor cannot be applied and the label shows (none); a run whose payload carries no probability map leaves that label\'s determinism unestablished rather than assumed',
    ...coverage.lines,
    '',
  ].join('\n');
  process.stdout.write(`${header}\n`);

  // A set that cannot contradict a constant-label model, or a run that would score a model other
  // than the pinned one, is a defect in the eval: both fail here instead of producing a number.
  const preflight: Array<string> = [];
  if (resolvedModel !== EXPECTED_MODEL_ID) {
    preflight.push(
      `model · pinned ${EXPECTED_MODEL_ID} but the resolved model is ${resolvedModel}; refusing to score a different model`,
    );
  }
  preflight.push(...coverage.failures);
  if (preflight.length > 0) {
    const lines = [
      `Result: FAIL — ${preflight.length} reason${preflight.length === 1 ? '' : 's'} (preflight; no case was run)`,
      ...preflight.map((failure) => `  ${failure}`),
    ];
    process.stdout.write(`${lines.join('\n')}\n`);
    return 1;
  }

  let scoringSet = caseSet;
  let control: Inversion | undefined;
  if (commandLine.negativeControl) {
    const inverted = invertOneExpectation(caseSet);
    scoringSet = inverted.caseSet;
    control = inverted.inversion;
    process.stdout.write(
      `control · negative control active · inverted ${control.caseId} · ${control.question}: expected ${control.from} → ${control.to}\n`,
    );
  }

  let deadlineTimer: NodeJS.Timeout | undefined;
  const deadline = new Promise<never>((_resolve, reject) => {
    deadlineTimer = setTimeout(
      () => reject(new Error(`eval deadline of ${DEADLINE_MS} ms exceeded before every case was scored`)),
      DEADLINE_MS,
    );
  });
  // A rejection that surfaces after the run already finished is not a second failure to report.
  deadline.catch(() => undefined);

  const client = new Client({ name: 'odd-adviser-classification-eval', version: '0.0.0' });
  const transport = new StdioClientTransport({
    command: NODE_COMMAND,
    args: [SERVER_ENTRY],
    cwd: PACKAGE_ROOT,
    env: environment,
  });

  const operation = new ScoreClassificationSet({
    evidenceEvaluator: new McpEvidenceEvaluator({
      client,
      expectedModel: EXPECTED_MODEL_ID,
      startedAt,
      deadlineMs: DEADLINE_MS,
      deadline,
    }),
  });

  const sessionFailures: Array<string> = [];
  let score: ClassificationScore | undefined;
  try {
    await Promise.race([client.connect(transport), deadline]);
    score = await operation.execute(scoringSet, {
      runs: commandLine.runs,
      confidenceFloor: CONFIDENCE_FLOOR,
    });
  } catch (error) {
    sessionFailures.push(`session · ${describeError(error)}`);
  } finally {
    if (deadlineTimer !== undefined) clearTimeout(deadlineTimer);
    await closeQuietly(client);
  }

  const failures: Array<string> = [...sessionFailures, ...(score?.failures ?? [])];
  const lines: Array<string> = [''];

  if (score !== undefined) {
    lines.push(...renderCaseResults(score));

    const unscored = buildUnscored(score.comparisons);
    if (unscored.length > 0) {
      lines.push('Unscored answers (printed, not asserted):');
      lines.push(...unscored.map((row) => `  ${row.question} · ${row.choice}: ${row.count}`));
    }

    lines.push('Confusion (expected × got, per run):');
    lines.push(
      ...buildConfusion(score.comparisons).map(
        (row) => `  ${row.question} · ${row.expected} × ${row.got}: ${row.count}`,
      ),
    );
  }

  // The control's own verdict: the inverted label must come back as a disagreement, otherwise the
  // harness has not shown it can fail and the control itself is reported as a failure.
  if (control !== undefined) {
    const label = score?.labels.find(
      (entry) => entry.caseId === control.caseId && entry.question === control.question,
    );
    const modal = label?.modal ?? MISSING;
    const proven = label !== undefined && label.modal === control.from;
    if (!proven) {
      failures.push(
        `control · inverted ${control.caseId} · ${control.question} still reported ${modal}; the harness has not shown it can report a disagreement`,
      );
    }
    lines.push(
      `control · inverted ${control.caseId} · ${control.question} ${control.from} → ${control.to} · modal ${modal} · ${proven ? 'the run fails on the inverted label and exits 1 as required' : 'no disagreement was reported, so the harness cannot prove it can fail'}`,
    );
  }

  const casesScored = score?.casesEvaluated ?? 0;
  const caseCount = score?.cases ?? caseSet.cases.length;
  const labelCount = score?.labels.length ?? 0;
  const observationTotal = score?.observations ?? 0;
  const runs = score?.runs ?? commandLine.runs;
  const runFacts =
    `cases scored ${casesScored}/${caseCount} · scored labels ${labelCount} · observations ${observationTotal} (${runs} per label) · run count ${runs} · model ${resolvedModel}`;

  lines.push('');
  if (failures.length === 0) {
    lines.push(
      `Result: PASS — ${runFacts} · every scored label returned one identical probability map across its runs, so this gateway was deterministic for this set on this invocation; this records agreement on this single run and is not a pass of the classifier.`,
    );
    process.stdout.write(`${lines.join('\n')}\n`);
    return 0;
  }

  lines.push(
    `Result: FAIL — ${runFacts} · ${failures.length} reason${failures.length === 1 ? '' : 's'}; this records disagreement on this run, which is not by itself a verdict on the classifier.`,
    ...failures.map((failure) => `  ${failure}`),
  );
  process.stdout.write(`${lines.join('\n')}\n`);
  return 1;
}

main().then(
  (exitCode) => {
    process.exitCode = exitCode;
  },
  (error) => {
    // A case-file defect, an unreadable file or a start-up failure: the literal reason, non-zero.
    process.stderr.write(`classification eval: ${describeError(error)}\n`);
    process.exitCode = 1;
  },
);

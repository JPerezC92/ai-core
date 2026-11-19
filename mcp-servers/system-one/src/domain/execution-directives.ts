// Domain rule: turn validated evidence answers into the System 1 execution directives
// delivered to System Two. Each directive is either derived from one validated answer or
// taken from the frozen action map below, so no supplied message text can reach the block.
// The unavailable block is the fixed text a failed evaluation is reported with. No IO, no
// infrastructure imports, no throws.

import type { DecisionChoice, ValidatedDecisionAnswer, ValidatedEvidenceAnswers } from "./decision-response.ts";
import { answerIds } from "./question-profile.ts";
import type { AnswerId } from "./question-profile.ts";

export const EXECUTION_DIRECTIVES_BLOCK_START = "=== SYSTEM 1 | EXECUTION DIRECTIVES ===";
export const EXECUTION_DIRECTIVES_UNAVAILABLE_BLOCK_START = "=== SYSTEM 1 | UNAVAILABLE ===";
export const EXECUTION_DIRECTIVES_BLOCK_END = "=== END SYSTEM 1 ===";

const EXECUTE_ACCORDINGLY =
	"Execute accordingly. Deviate only when stronger evidence or governing constraints justify it.";
const NO_NEW_PERMISSIONS = "No new permissions are granted.";
const UNAVAILABLE_NOTICE = "The System 1 evidence evaluation reported an error for this request.";

// An interrupt answer speaks to the turn itself, so it is included at a higher figure than
// the guidance answers that only qualify how the turn proceeds.
const INTERRUPT_INCLUSION_FIGURE = 0.8;
const GUIDANCE_INCLUSION_FIGURE = 0.6;

// The frozen action map: one fixed action sentence per (questionId, choice) pair. A pair
// absent from this map yields no directive, which is what keeps an unmapped answer — the
// derived `absent` visual-evidence state, for example — out of the block.
const FROZEN_ACTIONS: Readonly<Partial<Record<AnswerId, Readonly<Partial<Record<DecisionChoice, string>>>>>> = {
	scope_changed: {
		present:
			"Potential new requirement in this message. Check existing context and authorization before expanding. Pause only work that still needs extra authorization.",
		absent: "No new requirement in this message. Continue the established task without unnecessary renegotiation, respecting actual context and authorization.",
	},
	user_only_decision: {
		present:
			"A reserved decision is in this message. Ask that specific question. Continue independent authorized work; do not freeze the whole turn.",
		absent: "No reserved decision in this message. Continue already-authorized work. Do not ask for redundant approval. Not new permission.",
	},
	visual_evidence: {
		present: "Image attached. Inspect it before answering.",
	},
};

// One delivered directive: the answer it came from and the frozen action it maps to. The
// figure is the answer's reported score, unrounded; the block renders it to two decimals.
export type ExecutionDirective = {
	readonly questionId: AnswerId;
	readonly choice: DecisionChoice;
	readonly figure: number;
	readonly action: string;
};

// What the evaluation returns and the delivery edge forwards: the rendered block and the
// directives it was rendered from. An empty item set means there is nothing to inject, so
// the block is empty.
export type ExecutionDirectives = {
	readonly block: string;
	readonly items: ReadonlyArray<ExecutionDirective>;
};

function maximumProbability(probabilities: Readonly<Record<DecisionChoice, number>>): number | null {
	let maximum: number | null = null;
	for (const score of Object.values(probabilities)) {
		if (!Number.isFinite(score)) continue;
		if (maximum === null || score > maximum) maximum = score;
	}
	return maximum;
}

// The figure a directive reports is the answer's own confidence when it carries a finite
// one, and otherwise the strongest probability the answer recorded.
function reportedFigure(answer: ValidatedDecisionAnswer): number | null {
	const confidence = answer.confidence;
	if (confidence !== undefined && Number.isFinite(confidence)) return confidence;
	return maximumProbability(answer.probabilities);
}

// The figure an answer must reach to be included, or null when the pair is not in the
// frozen map and therefore yields no directive at all.
function inclusionFigure(questionId: AnswerId, choice: DecisionChoice): number | null {
	if (FROZEN_ACTIONS[questionId]?.[choice] === undefined) return null;
	const interrupts = questionId === "scope_changed" || questionId === "user_only_decision";
	return interrupts && choice === "present" ? INTERRUPT_INCLUSION_FIGURE : GUIDANCE_INCLUSION_FIGURE;
}

function directiveFor(questionId: AnswerId, answer: ValidatedDecisionAnswer): ExecutionDirective | null {
	const action = FROZEN_ACTIONS[questionId]?.[answer.choice];
	const threshold = inclusionFigure(questionId, answer.choice);
	const figure = reportedFigure(answer);
	if (action === undefined || threshold === null || figure === null) return null;
	if (figure < threshold) return null;
	return { questionId, choice: answer.choice, figure, action };
}

function findingLines(directive: ExecutionDirective): ReadonlyArray<string> {
	return [`${directive.questionId} → ${directive.choice} (${directive.figure.toFixed(2)})`, `→ ${directive.action}`];
}

function directivesBlock(items: ReadonlyArray<ExecutionDirective>): string {
	return [
		EXECUTION_DIRECTIVES_BLOCK_START,
		...items.flatMap(findingLines),
		EXECUTE_ACCORDINGLY,
		NO_NEW_PERMISSIONS,
		EXECUTION_DIRECTIVES_BLOCK_END,
	].join("\n");
}

// The projection over the closed answer vocabulary, so the directive order is the answer
// order rather than a record's insertion order. An empty item set yields an empty block:
// there is nothing for System Two to inject.
export function projectExecutionDirectives(answers: ValidatedEvidenceAnswers): ExecutionDirectives {
	const items: ExecutionDirective[] = [];
	for (const questionId of answerIds) {
		const answer = answers[questionId];
		if (answer === undefined) continue;
		const directive = directiveFor(questionId, answer);
		if (directive !== null) items.push(directive);
	}
	return { block: items.length === 0 ? "" : directivesBlock(items), items };
}

// The unavailable block: fixed text only, so an evaluation that failed carries no directive
// and no caller-supplied value into the delivered block.
export function unavailableExecutionDirectives(): ExecutionDirectives {
	return {
		block: [
			EXECUTION_DIRECTIVES_UNAVAILABLE_BLOCK_START,
			UNAVAILABLE_NOTICE,
			NO_NEW_PERMISSIONS,
			EXECUTION_DIRECTIVES_BLOCK_END,
		].join("\n"),
		items: [],
	};
}

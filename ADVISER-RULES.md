# Adviser rules

The rules the System 1 adviser must satisfy to be worth reading. Every rule is checkable; a
rule that cannot be checked is a preference, not a rule. Governs the adviser only.

- **Feature record:** `odd/tasks/2026-11-08-odd-adviser.md`
- **Profile:** `mcp-servers/system-one/profiles/odd-evidence-v4.json` — the profile the server loads today. v1–v3 are retained as history and are not loaded; a reader who opens v1 will see the `unknown` states R9 and R10 forbid, which is why v1 is not the reference here.
- **Adapter:** `.opencode/plugins/odd-adviser/src/index.ts`
- **Owner:** Cipher 🔓 (Lead Orchestrator)

A change that violates a rule below is a finding against that change, not a style question.

## 1. Purpose — it must help someone decide

**R1 — Every block names the decision it informs and the option it recommends.**
A receipt is not advice. *Check:* read the injected block; can a reader act differently because of it?

**R2 — Options, confidence and the question they answer travel in the block.**
The block carries choices, not only "an answer arrived". *Check:* the block shows at least one `question → choice (confidence)` triple.

**R3 — Advice is readable in under five seconds.**
One line per question, no prose padding, no restated question text. *Check:* the block is shorter than the message it comments on.

**R4 — Advice is input to a decision, never the decision.**
It never authorizes, waives a gate, blocks an action, or mutates state. *Check:* the block contains an explicit authority-boundary sentence and no imperative to act.

## 2. Workflow — it obeys ODD

**R5 — Advice about scope, authority or tracking is phrased in ODD steps and cites the scope it measured against.**
"Scope changed" is meaningless without the accepted scope. *Check:* the block names the step and the scope it compared.

**R6 — It creates no plan, status field, tracker or second record.**
The ODD feature document stays the sole task record. *Check:* no new file or status surface appears as a consequence of advising.

**R7 — Its own changes are tracked like any other work.**
Tracked before the first write; specs and tasks updated before affected code; the profile version is bumped, never edited in place. *Check:* the feature `## Log` cites the change, and an old evaluation record still resolves to the profile it ran against.

**R8 — It reads no repository state and writes no project file.**
The message and its inline images are the whole input. *Check:* the request payload contains no path, and no file is created while evaluating.

## 3. Evidence — no unverifiable answers

**R9 — No question may carry a state its input cannot reach.**
If the tool is not given the evidence a state requires, that state is decorative and will absorb every weak case. *Check:* for each state in the profile, name the input that can produce it.

**R10 — No general "unknown", "mixed" or "not applicable" bucket in any question.**
An all-purpose escape state dominates the distribution and hides the answer. *Check:* the profile's state list contains only discriminating states.

**R11 — Uncertainty is a number, not a verdict.**
The profile returns a choice plus probabilities; a low maximum is reported as weak signal, never as a non-answer and never as a third state. *Check:* inspect a weak case; a choice is still returned.

**R12 — No claim exceeds what the model returned.**
No citations, no "verified", no "secure to follow", no implied review. *Check:* every noun in the block is traceable to the response payload.

**R13 — Failure is explicit and bounded.**
A timeout, transport error, rejection or malformed payload produces a named status in the block — never silence, never a plausible substitute. *Check:* kill the MCP mid-session; the next message carries a bounded code.

**R14 — Delivery to the model is verified, not assumed.**
"Pushed onto the request" is not "read by the model". *Check:* a sentinel carried in the block is observed in the following model turn.

**R15 — Records are content-free by default.**
No raw prompt, image bytes, file contents or error text; coverage is reported as counts. *Check:* open the trace record for a known message and search for its text.

## 4. Cost and failure boundaries

**R16 — A slow call never delays the message.**
Bounded by a stated timeout, degrading to that timeout's status. *Check:* set the endpoint unreachable; the message still sends within the bound.

**R17 — Exactly one evaluation per message; continuations reuse it.**
Tool continuations re-inject the cached result. *Check:* one `evaluate_started` and one MCP record per user message, regardless of model calls in that turn.

## Current state (2026-11-08, after the v3/v4 profile work and the classification eval)

| Rule | State | Evidence |
|---|---|---|
| R1, R2 | ✅ holding | the block carries one `question → choice (confidence)` line per answered question, with a weak-signal marker below 0.60 (`plugin.test.ts` block assertions) |
| R9, R10, R11 | ✅ holding | every question has exactly `present`/`absent`; no general escape state exists in v4; uncertainty is reported as a probability and a weak marker, never as a third state |
| R3 | ✅ holding | one line per question, no restated question text |
| R12 | ⚠️ caveat | `visual_evidence` is now computed from the request, so the block prints a `1.00` figure for a fact no model judged; the payload does not distinguish judged from computed |
| R14 | ⚠️ unproven | a pushed `SystemPart` is observed in logs; no sentinel has been observed in the model's own context |
| R15 | ❌ violated | `output/system1/events.jsonl` still stores `request.state` — the raw message — verbatim |
| R4, R16, R17 | ✅ holding | boundary sentence present; bounded timeout; one `evaluate_started` per message with continuation reuse |
| R5, R6, R7, R13 | ✅ holding | ODD-phrased; no second tracker; tracked; bounded codes |
| R1–R13 (measured) | ✅ 37/37 | the live-model eval scored 37 model-judged labels with zero disagreements, 5 runs each, every probability map identical across runs; `visual_evidence` labels are excluded from that count because they are computed, not judged |

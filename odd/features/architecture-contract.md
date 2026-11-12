# Architecture contract

The single language-agnostic architecture contract that governs how domain, application and infrastructure responsibilities are modelled, organized and tested in every supported language, and how language and framework documentation specializes it without contradicting it.

**Status:** achieved

## Requirements

- [x] R1 `local` — Every application use case is a class exposing one `execute()` operation, with its required collaborators provided by constructor injection, in every supported language.
- [x] R2 `local` — The class requirement does not introduce an abstract base class, an interface for every class, an inheritance hierarchy without a polymorphic need, a forwarding service layer, or a pass-through wrapper.
- [x] R3 `local` — User-interface components, hooks and general-purpose utilities are not application use cases and are not turned into classes by the use-case requirement.
- [x] R4 `upstream · local detail` — A domain entity owns its applicable business invariants and legal transitions, a value object encapsulates its domain semantics, and a data-only record is used only where the type genuinely carries no identity-based behaviour or legal transition.
- [x] R5 `upstream · local detail` — A transformation governed by a business rule belongs to the domain, a transformation between an external representation and domain data belongs to the infrastructure boundary owning that representation, and an infrastructure adapter contains no business rule.
- [x] R6 `local` — Infrastructure adapter and outside-data mapping modules occupy `infrastructure/adapters/` and repository adapters occupy `infrastructure/repositories/`, each directory created only where its responsibility exists.
- [x] R7 `local` — The canonical directory organization is shared across languages within each application shape, so equivalent responsibilities are organised the same way in every language, while the backend, frontend and scripts shapes keep their own legitimate differences and each language keeps its own filename conventions.
- [x] R8 `local` — No presentation directory is a mandatory part of the canonical organization.
- [x] R9 `local` — Exactly three testing levels exist and no additional level is introduced.
- [x] R10 `local` — Every test lives under the root-level `tests/` directory in the `unit/`, `integration/` and `e2e/` level directories; no test is colocated with production code, no test lives inside a production directory, and no production file carries an obligation to have its own test.
- [x] R11 `local` — Nested test folders group tests by behavioural target, and no role-named nested folder is mandatory.
- [x] R12 `local` — A backend unit test exercises one application use-case class's `execute()` with its ports mocked and verifies the returned values and returned domain errors; a frontend unit test renders the component with its real hook, mocks the service module rather than the hook module, and verifies user-visible behaviour.
- [x] R13 `local` — A backend integration test exercises one repository adapter against a real isolated database and verifies the raw-record-to-domain-entity mapping; a frontend integration test exercises one service module with `fetch` stubbed and verifies the raw-JSON-to-typed-output mapping and the returned domain errors; a script or CLI integration test exercises one concrete adapter against an isolated dependency appropriate to its responsibility.
- [x] R14 `local` — An isolated parser or loader is an approved unit target only when its responsibility is converting an external representation into domain data, asserting mapping, coercion, extraction and the documented failure behaviour; it authorizes no independent unit test for an arbitrary helper, mapper, entity, value object or production file, and no parser or loader test directory is created.
- [x] R15 `local` — A backend end-to-end test exercises the assembled HTTP application and asserts the HTTP status and the response body contract; a frontend end-to-end test exercises the assembled browser application and asserts page behaviour, user-visible outcomes and the absence of uncaught page errors; a script or CLI end-to-end test exercises the assembled CLI or application entry point and asserts exit status, output and the relevant effects. The framework-specific mechanism of each end-to-end boundary stays in the applicable stack guide.
- [x] R16 `local` — The language-agnostic architectural rules are the authoritative statement of the architecture, and the application-shape guides and the language and framework guides specialize them without contradicting or redefining them.

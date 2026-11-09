import type { UserOnlyDecisionEvidence } from "../../domain/user-only-decision.ts";

const unspecified: UserOnlyDecisionEvidence = {
  text: null,
  hasInlineImage: false,
  authorizationIntent: "unspecified",
};

const authorized: UserOnlyDecisionEvidence = {
  text: "proceed with the assigned implementation",
  hasInlineImage: false,
  authorizationIntent: "authorize",
};

const discussionOnly: UserOnlyDecisionEvidence = {
  text: "i described a task but did not tell you to implement it",
  hasInlineImage: true,
  authorizationIntent: "unspecified",
};

export function create(
  overrides?: Partial<UserOnlyDecisionEvidence>,
): UserOnlyDecisionEvidence {
  return {
    ...unspecified,
    ...overrides,
  };
}

export function createMany(
  count: number,
  overrides?: Partial<UserOnlyDecisionEvidence>,
): UserOnlyDecisionEvidence[] {
  return Array.from({ length: count }, () => create(overrides));
}

export function present(
  overrides?: Partial<UserOnlyDecisionEvidence>,
): UserOnlyDecisionEvidence {
  return create({ ...authorized, ...overrides });
}

export function absent(
  overrides?: Partial<UserOnlyDecisionEvidence>,
): UserOnlyDecisionEvidence {
  return create({ ...discussionOnly, ...overrides });
}

export function unknown(
  overrides?: Partial<UserOnlyDecisionEvidence>,
): UserOnlyDecisionEvidence {
  return create({ ...unspecified, ...overrides });
}

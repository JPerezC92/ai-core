export type UserOnlyDecisionClassification = "present" | "absent" | "unknown";

export type UserOnlyDecisionEvidence = {
  readonly text: string | null;
  readonly hasInlineImage: boolean;
  readonly authorizationIntent: "authorize" | "decline" | "unspecified";
};

export function classifyUserOnlyDecision(
  evidence: UserOnlyDecisionEvidence,
): UserOnlyDecisionClassification {
  switch (evidence.authorizationIntent) {
    case "authorize":
      return "present";
    case "decline":
      return "absent";
    case "unspecified":
      return evidence.text === null ? "unknown" : "absent";
  }
}

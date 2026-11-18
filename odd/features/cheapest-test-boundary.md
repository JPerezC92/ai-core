# Cheapest proving test boundary

Tests prove a contract at the least expensive boundary that still detects the intended regression, so unique coverage is kept and redundant expensive execution is not.

**Status:** partial

## Requirements

- [ ] R1 — A test exercises the least expensive boundary that still proves its intended contract.
- [x] R2 — Adding or substantially expanding an integration or end-to-end test that performs real external operations requires a concise justification that the cheaper boundary is insufficient.
- [x] R3 — Identical assertions are not repeated across unit, integration, and end-to-end layers unless the different boundary supplies additional regression protection.
- [x] R4 — Critical integration boundaries are not replaced with mocks solely to make tests faster.

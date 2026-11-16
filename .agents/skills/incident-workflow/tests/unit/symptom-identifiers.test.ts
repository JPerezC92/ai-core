import { describe, expect, it } from 'vitest';

import { isLocalSymptomId, isSymptomId, parseSymptomReferences } from '#scripts/incident_workflow_pkg/domain/symptom-id.ts';

describe('symptom identifiers', () => {
  it('accepts a baseline class id', () => {
    expect(isSymptomId('S-01')).toBe(true);
    expect(isLocalSymptomId('S-01')).toBe(false);
  });

  it('accepts a destination-owned class id', () => {
    expect(isSymptomId('LOCAL:S-01')).toBe(true);
    expect(isLocalSymptomId('LOCAL:S-01')).toBe(true);
  });

  it('rejects a substring match', () => {
    expect(isSymptomId('XS-01')).toBe(false);
    expect(isSymptomId('S-01x')).toBe(false);
  });

  it('rejects a malformed local prefix', () => {
    expect(isSymptomId('local:S-01')).toBe(false);
    expect(isSymptomId('LOCAL-S-01')).toBe(false);
  });

  it('keeps an open-ended numeric width', () => {
    expect(isSymptomId('S-123')).toBe(true);
    expect(isSymptomId('LOCAL:S-1234')).toBe(true);
  });

  it('parses a comma-separated cell into complete tokens', () => {
    expect(parseSymptomReferences('S-05, LOCAL:S-01')).toEqual({ tokens: ['S-05', 'LOCAL:S-01'], invalid: [] });
  });

  it('reports the segments that are not whole identifiers', () => {
    expect(parseSymptomReferences('S-05, unclassified, S-')).toEqual({
      tokens: ['S-05'], invalid: ['unclassified', 'S-'],
    });
  });

  it('ignores empty segments', () => {
    expect(parseSymptomReferences(' S-05 , ')).toEqual({ tokens: ['S-05'], invalid: [] });
  });
});

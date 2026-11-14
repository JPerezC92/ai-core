// Connection lifecycle of the stdio MCP adapter: a rejected attempt is dropped so a later
// evaluation reconnects, concurrent evaluations share one attempt, and a failed handshake
// releases the client and the transport it may have spawned.

import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';

// Shared, hoisted state so the module factories below can observe and steer the fakes without
// importing the code under test. Nothing here starts a process: the SDK client and transport
// are replaced entirely.
const sdk = vi.hoisted(() => ({
  connectAttempts: 0,
  failConnectures: 0,
  closedClients: 0,
  closedTransports: 0,
  gate: undefined as Promise<void> | undefined,
}));

vi.mock('@modelcontextprotocol/client', () => ({
  Client: class {
    async connect(): Promise<void> {
      sdk.connectAttempts += 1;
      if (sdk.gate !== undefined) await sdk.gate;
      if (sdk.connectAttempts <= sdk.failConnectures) throw new Error('handshake failed');
    }

    async callTool(): Promise<{ structuredContent: unknown }> {
      return {
        structuredContent: {
          ok: true,
          profileId: 'fixture-profile',
          profileVersion: 1,
          answers: { q1: { type: 'choice', choice: 'yes', probabilities: { yes: 1 } } },
        },
      };
    }

    async close(): Promise<void> {
      sdk.closedClients += 1;
    }
  },
}));

vi.mock('@modelcontextprotocol/client/stdio', () => ({
  StdioClientTransport: class {
    async close(): Promise<void> {
      sdk.closedTransports += 1;
    }
  },
}));

const { createStdioMcpClient } = await import('./stdio-mcp-client.ts');

const OPTIONS = { command: 'node', args: ['entry.ts'], cwd: '.' } as const;
const INPUT = { text: 'evidence', images: [] } as const;
const LIMIT = { timeoutMs: 1_000 } as const;

beforeEach(() => {
  sdk.connectAttempts = 0;
  sdk.failConnectures = 0;
  sdk.closedClients = 0;
  sdk.closedTransports = 0;
  sdk.gate = undefined;
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('failed connection retention', () => {
  test('reconnects after an initial connection failure', async () => {
    sdk.failConnectures = 1;
    const connection = createStdioMcpClient({ ...OPTIONS });

    const first = await connection.evaluate({ ...INPUT }, { ...LIMIT });
    const second = await connection.evaluate({ ...INPUT }, { ...LIMIT });

    expect(first).toStrictEqual({ status: 'unavailable', code: 'transport_error' });
    expect(second.status).toBe('evaluated');
    expect(sdk.connectAttempts).toBe(2);
  });
});

describe('concurrent connection attempts', () => {
  test('shares one attempt between concurrent evaluations', async () => {
    let release: () => void = () => undefined;
    sdk.gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    const connection = createStdioMcpClient({ ...OPTIONS });

    const evaluations = [
      connection.evaluate({ ...INPUT }, { ...LIMIT }),
      connection.evaluate({ ...INPUT }, { ...LIMIT }),
    ];
    release();
    const outcomes = await Promise.all(evaluations);

    expect(outcomes.map((outcome) => outcome.status)).toStrictEqual(['evaluated', 'evaluated']);
    expect(sdk.connectAttempts).toBe(1);
  });
});

describe('failed initialization cleanup', () => {
  test('releases the client and transport when the handshake fails', async () => {
    sdk.failConnectures = 1;
    const connection = createStdioMcpClient({ ...OPTIONS });

    await connection.evaluate({ ...INPUT }, { ...LIMIT });

    expect(sdk.closedClients).toBe(1);
    expect(sdk.closedTransports).toBe(1);
  });

  test('leaves the successful client open for reuse', async () => {
    const connection = createStdioMcpClient({ ...OPTIONS });

    await connection.evaluate({ ...INPUT }, { ...LIMIT });
    await connection.evaluate({ ...INPUT }, { ...LIMIT });

    expect(sdk.connectAttempts).toBe(1);
    expect(sdk.closedClients).toBe(0);
    expect(sdk.closedTransports).toBe(0);
  });
});

// End-to-end test of the assembled System 1 server: the real entry point src/mcp/stdio.ts
// is spawned as a real `node` child process, configured only through its documented
// environment variables, and driven by a real MCP client over stdio. A controlled local
// HTTP stub on an ephemeral loopback port stands in for the model endpoint and answers the
// request shape the decision gateway actually sends, so no developer's model server or
// machine state participates. Each case owns its temporary profile, trace and image
// locations; its child process and HTTP listener are torn down afterwards.

import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";
import { expect, test } from "vitest";

import { createQuestionProfile } from "#test/question-profile.factory.ts";

const STDIO_ENTRY = fileURLToPath(new URL("../../src/mcp/stdio.ts", import.meta.url));
const TOOL_NAME = "evaluate_odd_evidence";
const CONFIGURED_MODEL = "system-one-e2e-model";
const EVIDENCE_TEXT = "The latest user request repeats the accepted implementation scope.";

const DIRECTIVES_BLOCK_START = "=== SYSTEM 1 | EXECUTION DIRECTIVES ===";
const UNAVAILABLE_BLOCK_START = "=== SYSTEM 1 | UNAVAILABLE ===";

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readRecord(value: unknown, message: string): Record<string, unknown> {
	expect(isRecord(value), message).toBe(true);
	if (!isRecord(value)) throw new Error(message);
	return value;
}

// One stub answer in the shape the wired gateway forwards; the same two-state scores the
// profile declares, so a valid body passes validation.
function createDecisionAnswer(choice: "present" | "absent") {
	const probabilities: Record<"present" | "absent", number> = { present: 0.1, absent: 0.1 };
	probabilities[choice] = 0.8;
	return { type: "choice", choice, probabilities, confidence: 0.8 };
}

function createValidDecision(model: string) {
	return {
		model,
		answers: {
			scope_changed: createDecisionAnswer("present"),
			user_only_decision: createDecisionAnswer("absent"),
		},
		usage: { input_tokens: 0, output_tokens: 0 },
	};
}

// A contract-invalid decision: the endpoint answered, but the body omits one asked
// question, so the operation refuses to deliver it and returns the fixed unavailable
// directives instead of a decision.
function createInvalidDecision(model: string) {
	return {
		model,
		answers: { scope_changed: createDecisionAnswer("present") },
		usage: { input_tokens: 0, output_tokens: 0 },
	};
}

type DecisionStub = {
	readonly endpoint: string;
	readonly requests: ReadonlyArray<Record<string, unknown>>;
	close(): Promise<void>;
};

// A real HTTP listener on an ephemeral loopback port. It records every request body and
// answers from that body, so the configured model is observable at the endpoint and the
// server under test is the only one that could have addressed it.
async function startDecisionStub(decide: (request: Record<string, unknown>) => unknown): Promise<DecisionStub> {
	const requests: Array<Record<string, unknown>> = [];
	const server = createServer((request, response) => {
		const chunks: Buffer[] = [];
		request.on("data", (chunk: Buffer) => chunks.push(chunk));
		request.on("end", () => {
			const body = readRecord(
				JSON.parse(Buffer.concat(chunks).toString("utf8")),
				"the stub received a JSON body",
			);
			requests.push(body);
			response.writeHead(200, { "content-type": "application/json" });
			response.end(JSON.stringify(decide(body)));
		});
	});
	await new Promise<void>((resolve, reject) => {
		server.once("error", reject);
		server.listen(0, "127.0.0.1", () => resolve());
	});
	const address = server.address() as AddressInfo;
	return {
		endpoint: `http://127.0.0.1:${address.port}`,
		get requests() {
			return requests.slice();
		},
		close: () =>
			new Promise<void>((resolve, reject) => {
				server.close((error) => (error ? reject(error) : resolve()));
			}),
	};
}

type EvaluationWorkspace = {
	readonly profilePath: string;
	readonly tracePath: string;
	readonly imageDirectory: string;
	remove(): Promise<void>;
};

// A real temporary profile document plus the trace and image locations the server writes.
async function createWorkspace(): Promise<EvaluationWorkspace> {
	const directory = await mkdtemp(join(tmpdir(), "system-one-e2e-"));
	const profilePath = join(directory, "odd-evidence-profile.json");
	await writeFile(profilePath, JSON.stringify(createQuestionProfile()), "utf8");
	return {
		profilePath,
		tracePath: join(directory, "trace", "events.jsonl"),
		imageDirectory: join(directory, "images"),
		remove: () => rm(directory, { recursive: true, force: true }),
	};
}

// The server's configuration arrives only through its documented environment variables;
// the ambient environment is inherited so the interpreter can start, and every System One
// variable is set here, so no developer configuration can leak into the case.
function createEnvironment(endpoint: string, workspace: EvaluationWorkspace): Record<string, string> {
	const environment: Record<string, string> = {};
	for (const [key, value] of Object.entries(process.env)) {
		if (value !== undefined) environment[key] = value;
	}
	return {
		...environment,
		SYSTEM_ONE_ENDPOINT: endpoint,
		SYSTEM_ONE_MODEL: CONFIGURED_MODEL,
		SYSTEM_ONE_PROFILE: workspace.profilePath,
		SYSTEM_ONE_TIMEOUT_MS: "5000",
		SYSTEM_ONE_TRACE_PATH: workspace.tracePath,
		SYSTEM_ONE_IMAGE_DIR: workspace.imageDirectory,
	};
}

type RunningServer = {
	readonly client: Client;
	close(): Promise<void>;
};

// Spawn the real entry point as a child process and complete the MCP handshake. A failed
// handshake tears the transport down before the error is rethrown, so no child survives it.
async function startServer(endpoint: string, workspace: EvaluationWorkspace): Promise<RunningServer> {
	const transport = new StdioClientTransport({
		command: process.execPath,
		args: [STDIO_ENTRY],
		env: createEnvironment(endpoint, workspace),
		stderr: "pipe",
	});
	const client = new Client({ name: "system-one-e2e", version: "0.0.0" });
	try {
		await client.connect(transport);
	} catch (error) {
		await transport.close().catch(() => undefined);
		throw error;
	}
	return {
		client,
		close: () => client.close(),
	};
}

test("lists and serves one complete evidence evaluation over real stdio", async () => {
	const workspace = await createWorkspace();
	const stub = await startDecisionStub((request) => createValidDecision(String(request["model"])));
	let server: RunningServer | undefined;
	try {
		server = await startServer(stub.endpoint, workspace);

		const tools = await server.client.listTools();
		expect(tools.tools.map((tool) => tool.name)).toContain(TOOL_NAME);

		const result = await server.client.callTool({
			name: TOOL_NAME,
			arguments: { text: EVIDENCE_TEXT, images: [] },
		});

		expect(result.isError).toBeFalsy();
		const evaluation = readRecord(result.structuredContent, "the tool returned structured content");
		expect(evaluation["ok"]).toBe(true);

		const directives = readRecord(evaluation["directives"], "the result carries the directives record");
		const block = directives["block"];
		expect(typeof block).toBe("string");
		expect((block as string).startsWith(DIRECTIVES_BLOCK_START)).toBe(true);
		const items = Array.isArray(directives["items"]) ? directives["items"] : [];
		expect(
			items.some(
				(item) => isRecord(item) && item["questionId"] === "scope_changed" && item["choice"] === "present",
			),
		).toBe(true);

		// The configured model reached the stub, so configuration flowed only through the
		// documented environment variables.
		expect(stub.requests).toHaveLength(1);
		expect(stub.requests[0]?.["model"]).toBe(CONFIGURED_MODEL);
	} finally {
		await closeServer(server);
		await stub.close();
		await workspace.remove();
	}
});

test("returns the fixed unavailable directives when the decision is refused", async () => {
	const workspace = await createWorkspace();
	const stub = await startDecisionStub((request) => createInvalidDecision(String(request["model"])));
	let server: RunningServer | undefined;
	try {
		server = await startServer(stub.endpoint, workspace);

		const result = await server.client.callTool({
			name: TOOL_NAME,
			arguments: { text: EVIDENCE_TEXT, images: [] },
		});

		expect(result.isError).toBeFalsy();
		const evaluation = readRecord(result.structuredContent, "the tool returned structured content");
		expect(evaluation["ok"]).toBe(false);

		const directives = readRecord(evaluation["directives"], "the rejection carries the directives record");
		const block = directives["block"];
		expect(typeof block).toBe("string");
		expect((block as string).startsWith(UNAVAILABLE_BLOCK_START)).toBe(true);
		expect(directives["items"]).toStrictEqual([]);

		// The configured endpoint and model reached this case's own stub exactly once, so the
		// refusal was produced by the stub's answered body and not by an unconfigured default
		// endpoint: an ignored SYSTEM_ONE_ENDPOINT would leave the stub untouched here.
		expect(stub.requests).toHaveLength(1);
		expect(stub.requests[0]?.["model"]).toBe(CONFIGURED_MODEL);
	} finally {
		await closeServer(server);
		await stub.close();
		await workspace.remove();
	}
});

// Teardown is best-effort only for the child process: a server that never started, or one
// whose process already exited, must not turn a completed assertion into a teardown error.
async function closeServer(server: RunningServer | undefined): Promise<void> {
	if (server === undefined) return;
	await server.close().catch(() => undefined);
}

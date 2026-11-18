/**
 * Delivery: the destination a synchronization run resolved.
 *
 * A run that raises a boundary exception never reaches the operation's return
 * value, so the delivery edge — which owns the operator's channels — has no
 * outcome to read the destination from when it renders the failure. The
 * application operation resolves its destination through the filesystem probe it
 * is given, so the composition root hands it this probe: it answers every
 * question with the real one and remembers the destination path the run resolved.
 * Nothing is decided here, and no question is answered differently; the recorded
 * path labels the failure the operator reads and nothing else.
 */

import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";

export class RunDestinationProbe implements FilesystemProbe {
	readonly #files: FilesystemProbe;
	#destination: string | null = null;

	constructor(files: FilesystemProbe) {
		this.#files = files;
	}

	/**
	 * The path the run resolved as its destination, or `null` when it resolved
	 * none before the run stopped.
	 */
	get destination(): string | null {
		return this.#destination;
	}

	resolve(path: string): string {
		const resolved = this.#files.resolve(path);
		// The run resolves its destination before any other path work, so the first
		// resolved path is the destination it acts on.
		if (this.#destination === null) {
			this.#destination = resolved;
		}
		return resolved;
	}

	isDirectory(path: string): Promise<boolean> {
		return this.#files.isDirectory(path);
	}

	isFile(path: string): Promise<boolean> {
		return this.#files.isFile(path);
	}

	isInside(root: string, path: string): boolean {
		return this.#files.isInside(root, path);
	}
}

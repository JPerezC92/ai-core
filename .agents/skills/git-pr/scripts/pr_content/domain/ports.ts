/** Domain-owned capability contracts for supplied text and exclusive artifact creation. */

/**
 * Reads the text supplied at a caller-named path.
 *
 * The implementation performs no newline translation: it returns the stored bytes decoded as UTF-8.
 * A missing or unreadable path is a boundary failure, so it is thrown, not returned.
 */
export type SuppliedTextReader = (path: string) => string;

/**
 * Creates a new artifact at the caller-named path without overwriting an existing artifact.
 *
 * The capability owns exclusive creation only; deciding whether an artifact may be created is the
 * application's rule. An existing artifact or an unusable parent directory is a boundary failure,
 * so it is thrown rather than returned as a business rejection.
 */
export type ExclusiveArtifactWriter = (path: string, content: string) => void;

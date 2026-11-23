# TypeScript module resolution and import standard

How TypeScript modules in this repository and in destination projects name their targets: the source-extension rule, the private alias mechanism, workspace dependencies through public entry points, and the distinct requirements of directly executed, bundled and compiled packages.

**Status:** partial

## Requirements

- [x] R1 — Every intra-package source specifier names its target with its TypeScript source extension, for both relative and aliased references, and parent-directory traversal is not used.
- [x] R2 — A package uses one declared alias mechanism as its preferred form for cross-directory references, accepts the same-package child-directory relative form, keeps parent-directory traversal out of its specifiers, and does not let a relative specifier's target depend on the importing file's depth beyond descending into its own child directories.
- [x] R3 — A package consumed by another package is addressed only through its declared public entry points, never through its internal source or build paths and never through a compiler-only alias.
- [x] R4 — Each production mode states the mechanism its own pipeline resolves, distinguishing direct execution, bundling and compiled output instead of imposing one configuration everywhere.
- [x] R5 — A directly executed package runs its own TypeScript sources without a build step and without an additional alias loader.
- [ ] R6 — A compiled package emits JavaScript and declarations that consumers can use, with its internal aliases still resolving after compilation.
- [x] R7 — An alias mechanism is permitted only where the selected build or runtime pipeline actually resolves it; successful type checking alone does not establish that support.
- [x] R8 — The standard reaches destination projects alongside the code it governs, while the mechanism a specific project selects stays project-owned.

# Repo Policy (Non-Negotiable)

This repo is a **trust anchor**. Treat it like an ABI + test vectors + spec, not a dev workspace.

## Allowed changes

- Add new assets under new, versioned paths.
- Add new schema versions as new files.
- Update `SHA256SUMS.txt` files to include newly added files.
- Update top-level docs (`README.md`, `POLICY.md`) to clarify usage.

## Forbidden changes

- Modifying or deleting already-published assets in:
  - `schemas/**` (except `schemas/SHA256SUMS.txt`)
  - `contracts/**` (except `contracts/SHA256SUMS.txt`)
  - `bundles/**` (except `**/SHA256SUMS.txt`)
- Renaming existing published files (breaks pins).

If you need to “fix” something: **publish a new version** in a new path and leave the old one intact.

## Release discipline

Every published directory is expected to be self-contained:

- `SHA256SUMS.txt` is present and validates every file in that directory.
- Any bundle zip has a clear authenticity anchor (e.g., a published `bundle_sha256` token) and a scriptable verify path.


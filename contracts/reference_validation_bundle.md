# Verification and Trust Model

Every Helix release publishes a **reference validation bundle**: a deterministic archive containing **signed validation verdicts** + a bundle index so anyone can verify “this release passed the public validation packs” without cloning the repo.

## Download (GitHub Releases)

Pick the bundle for your platform from the release assets:

- `helix-reference-validation-bundle-<TAG>-linux.tar.gz`
- `helix-reference-validation-bundle-<TAG>-macos.tar.gz`
- `helix-reference-validation-publisher-<TAG>-linux.pub` / `…-macos.pub` (optional pinned pubkey; lets you avoid trusting the bundle’s embedded key)

Example (GitHub CLI):

```bash
gh release download <TAG> --repo omniscoder/Helix --pattern "helix-reference-validation-bundle-<TAG>-linux.tar.gz"
```

Copy/paste download + verify (curl):

```bash
TAG=<TAG>
curl -fL -o "helix-reference-validation-bundle-${TAG}-linux.tar.gz" "https://github.com/omniscoder/Helix/releases/download/${TAG}/helix-reference-validation-bundle-${TAG}-linux.tar.gz"
curl -fL -o "helix-reference-validation-publisher-${TAG}-linux.pub" "https://github.com/omniscoder/Helix/releases/download/${TAG}/helix-reference-validation-publisher-${TAG}-linux.pub"
helix verify bundle "helix-reference-validation-bundle-${TAG}-linux.tar.gz" --pubkey "helix-reference-validation-publisher-${TAG}-linux.pub" --json-out verify_bundle.json
```

macOS:

```bash
TAG=<TAG>
curl -fL -o "helix-reference-validation-bundle-${TAG}-macos.tar.gz" "https://github.com/omniscoder/Helix/releases/download/${TAG}/helix-reference-validation-bundle-${TAG}-macos.tar.gz"
curl -fL -o "helix-reference-validation-publisher-${TAG}-macos.pub" "https://github.com/omniscoder/Helix/releases/download/${TAG}/helix-reference-validation-publisher-${TAG}-macos.pub"
helix verify bundle "helix-reference-validation-bundle-${TAG}-macos.tar.gz" --pubkey "helix-reference-validation-publisher-${TAG}-macos.pub" --json-out verify_bundle.json
```

## Verify (one command)

```bash
helix verify bundle helix-reference-validation-bundle-<TAG>-linux.tar.gz --json-out verify_bundle.json
```

Behavior:

- Verifies every `verdict.json` signature (canonicalization is whitespace/key-order proof).
- If `bundle.index.json` is present, also enforces:
  - each verdict file’s `sha256`
  - each verdict’s `expectedStatus`
- Exits nonzero if any verdict fails verification or does not match the bundle index.

Optional pinned pubkey verification (stronger trust handshake):

```bash
gh release download <TAG> --repo omniscoder/Helix --pattern "helix-reference-validation-publisher-<TAG>-linux.pub"
helix verify bundle helix-reference-validation-bundle-<TAG>-linux.tar.gz --pubkey helix-reference-validation-publisher-<TAG>-linux.pub --json-out verify_bundle.json
```

## What’s inside the bundle

- `publisher.pub` (the public key for the bundle’s verdict signatures)
- `bundle.index.json` (verdict inventory + `sha256` + expected status + provenance like `gitSha`, `helixVersion`, `workflowRunUrl`, `builtAtUtc`)
- `verdicts/**/verdict.json` (signed verdict artifacts)
- `verdicts/**/verdict.summary.txt` (human-readable summaries)
- `packs/` + `packs.manifest.json` (pack manifest copies + integrity hashes)

## What failures mean

- Signature failure: the verdict was not produced by the bundle’s publisher key (or it was modified).
- SHA mismatch vs `bundle.index.json`: the verdict file bytes differ from the release inventory.
- Status mismatch vs `bundle.index.json`: the verdict is signed but does not match the release’s declared expected outcome.

## Expected failures (negative controls)

Some packs ship a `--case negative` that is intentionally wrong to exercise `--explain` and mismatch reporting. These runs are **expected-failure passes** and the CLI prints an explicit banner (`EXPECTED FAILURE PASS`) so screenshots don’t look like breakage.

## Interpreting `--json-out`

`helix verify bundle … --json-out verify_bundle.json` writes a machine report:

- `ok`: overall pass/fail
- `counts`: `{ok, fail, missing, total}`
- `results[]`: one entry per verdict with fields like `verdictFile`, `status`, `expectedStatus`, `signatureOk`, `shaOk`, `statusOk`

This JSON is intended for CI gates and (later) Teams/Enterprise acceptance checks.

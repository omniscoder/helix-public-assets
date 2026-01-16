# Enzyme Program Contract v1.0.0 — Golden Bundle

This directory is a self-contained, immutable test vector for external verification.

Contents

- `golden_bundle.zip`: the artifact bundle (zip)
- `golden_bundle.zip.sha256`: the expected **bundle_sha256** token (for `helix-cli enzyme verify --expected-bundle-sha256 …`)
- `SHA256SUMS.txt`: SHA-256 of the **file bytes** in this directory (use `sha256sum -c`)
- `golden_config.json`, `golden_policy.json`: deterministic inputs used to build the golden bundle
- `RELEASE_NOTES_enzyme-contract-v1.0.0.md`: contract freeze notes + expected bundle SHA

Verification (no Helix required)

```bash
sha256sum -c SHA256SUMS.txt
python3 ../../../../tools/verify_artifact_bundle.py golden_bundle.zip
```


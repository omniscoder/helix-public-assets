# Helix Demo Bundle (CRISPR) — v1.1.5

Deterministic demo output generated via:

`helix demo run --demo-id crispr --outdir <outdir> --zip`

Files

- `demo_crispr_bundle.zip`: artifact bundle zip (includes `reports/` HTML)
- `demo_crispr_bundle.zip.sha256`: expected `bundle_sha256` token (from the bundle manifest)
- `SHA256SUMS.txt`: SHA-256 of the file bytes in this directory

Verify

```bash
sha256sum -c SHA256SUMS.txt
python3 ../../../../../tools/verify_artifact_bundle.py demo_crispr_bundle.zip
```


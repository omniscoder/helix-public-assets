# Helix Trust Kit (two-minute proof)

This is the single entry point for auditors, partner engineers, and reviewers. One command, one diagram, one checklist.

> A Helix proof kit is a self-contained, deterministic replay bundle. Anyone can run it to reproduce exactly what we saw, verify all outputs cryptographically, and detect any drift.

## 1) One command
```bash
helix trust check --backend cpu-reference
```
What it does: runs the canonical repro spec twice under the pinned policy, normalizes timestamps, and compares hashes. Determinism + policy compliance in one go.

Expected output (happy path):
```
TRUST CHECK: PASS (cpu-reference, hash=…)
Policy: sha256:<hash> (audit-strict.json)
Locale: LC_ALL=C.UTF-8 LANG=
```
Failure semantics (built-in): prints first diff path, backend, locale, and policy hash so a ticket has all the evidence.

## 2) One diagram (static)
```
Spec → Policy (pinned under policies/) → Run (D-class) → Artifact header
                                          │
                                          └→ Trust Check (trust-check/v1) → PASS/FAIL
```
- Determinism enforced in run (seeded, locale fixed) and compared in trust check.
- escape hatch (`HELIX_ALLOW_UNPINNED_POLICY=1`) downgrades compliance: run is “not D2 pinned compliant.”

## 3) Compliance checklist (binary)
- Policy file lives under `policies/` (pinned); `policyHash`, `policyName`, `policyPath`, `determinismClass`, `trustCheckVersion` present in artifact header.
- `trust-check/v1` recorded in headers.
- Profile used: `audit-strict` (or documented exception) with `HELIX_POLICY_PATH` set.
- Locale fixed (C.UTF-8) during execution and verification.
- CI `trust-smoke` job passed (cpu-reference; native-cpu when available); docs build required.

## 4) GPU determinism envelope
- Class-of-failure: two “identical” GPU runs diverge because TF32/fast-math or a driver bump changes math. Helix records math-mode + GPU identity in headers and fails verification if the fingerprint is incomplete.
- **Guarantee:** GPU runs are deterministic only within documented tolerances (D1/D2) when executed on the *same GPU architecture, driver range, and math mode* as recorded in the artifact header.
- **Conditions:** use the recorded backend class, SM family/driver versions captured in `env_fingerprint`, and deterministic math flags (no TF32/fast-math unless explicitly allowed by policy).
- **Non-guarantees:** no promise of byte-identical results across GPU vendors, across major driver branches, or across distinct GPU architectures; cross-vendor parity is out of scope.
- **Enforcement:** `helix trust check` now fails GPU artifacts whose backend fingerprint is incomplete (driver/runtime/UUID/compute-capability/math-mode flags required).
- **Compatibility:** GPU fingerprint schema version is `backend-fingerprint/v1`; adding new required fields is a version bump.
- Evidence bundle: run `python tools/smoke_cuda.py --out artifacts/gpu_envelope_proof` (or CI `gpu-envelope-proof` artifact) for a self-contained backend.json + receipt + verify.txt.

## 5) escape hatch note
If `HELIX_ALLOW_UNPINNED_POLICY=1` is set, the run intentionally bypasses the pinned-policy requirement. Treat such runs as non-compliant for D2 audits and expect taint/annotations in reports.

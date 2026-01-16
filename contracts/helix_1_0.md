# Helix 1.0 Contract

This document defines what “Helix 1.0” means. If the acceptance checklist passes, we ship. If not, we do not ship.

## Scope

Helix 1.0 is a simulation first in silico environment. No wet lab instructions or biological manipulation guidance is provided or required.

Helix 1.0 includes:
1. Helix Engine (CPU reference and native backends, optional GPU backend)
2. Helix CLI (headless run and export)
3. Helix Studio (UI for building, running, inspecting, cloning, exporting)
4. Provenance and artifacts (schemas, versioning, reproducibility)

## Non goals for 1.0

1. Adding new simulation models
2. Adding new UI modes, panels, or visual metaphors
3. Expanding dataset catalog beyond what is needed for acceptance tests
4. Performance chasing beyond “not egregiously slow”

Feature work resumes after 1.0.

## Definitions

Determinism
Same inputs and same seed produce identical artifacts and summaries, within declared tolerances for floating point.

Artifact
Any file emitted by CLI or Studio export, including run meta, summaries, plots, and snapshots.

Backend
A compute implementation, such as cpu reference, native cpu, or gpu.

## Acceptance checklist

### Engine correctness and determinism

A. CPU reference and native cpu agree on outcomes for the golden suite.
B. Deterministic artifacts for the golden suite.
C. If gpu backend is enabled, it matches cpu reference within declared tolerances for the gpu suite.

GPU backend is validated against CPU reference via a minimal golden suite but is not part of the default CI gate.

### Studio reliability

A. Open project, run sim, inspect outcomes, scrub timeline.
B. Clone a run and confirm lineage is preserved.
C. Export snapshot produces PNG and JSON and can be reproduced.
D. No UI deadlock or hang in the golden suite path.

### CLI reliability

A. `helix run` works headless for golden suite.
B. `helix export` produces same artifact set as Studio export.
C. Exit codes are meaningful.

### Schemas and provenance

A. All emitted JSON includes schema version fields.
B. Backward compatibility policy documented.
C. Validator exists for artifacts.

### CI and release

A. Unit tests green.
B. Visual regression green.
C. Docs build green with strict warnings.
D. Release dry run passes: build wheel, install in clean env, run golden suite.

## Golden suites

### golden cpu suite
Small deterministic suite used on every PR and in CI.

### golden ui suite
Studio scripted or semi scripted path validated via layout and screenshot checks.

### golden gpu suite
Minimal suite for at least one gpu lane, even if only on self hosted runner.

## Required commands

1. Unit tests
   - Linux/macOS: `tools/test.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File tools/test.ps1`

2. CLI smoke
   `helix run --backend cpu-reference <golden config> <out session>`
   `helix export --session <out session> --run-id <run id> --outdir <out dir>`

3. Studio smoke
   Launch Studio, open golden project, execute scripted path if available.

4. Artifact validation
   `python tools/validate_artifacts.py <out dir>`

## Release criteria

A tag named v1.0.0 must not be created until the acceptance checklist is green in CI.

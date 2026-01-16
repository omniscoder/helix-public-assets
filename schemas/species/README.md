# species_detection_v1

Purpose: portable, deterministic species hypothesis artifact emitted by `helix_engine.species_detect`.

Top-level fields
- `schema`: must equal `species_detection_v1`.
- `created_at_utc`: ISO8601 UTC timestamp.
- `db_bundle_id`, `db_bundle_hash`: identify the reference bundle.
- `params`: detection parameters (k, sketch_size, sampling strides, thresholds).
- `backend`: backend used (cpu / cpu-fallback / cuda).
- `inputs`: input counts + digest.
- `sketch`: query sketch metadata + digest.
- `hypotheses`: species-level candidates with scores/posterior.
- `genus_hypotheses`: genus aggregation (optional).
- `resolution`: resolved / unresolved / mixed / genus summary.
- `novelty`: novelty flag (optional).
- `blocking_issues`: policy gating reasons (optional).

Determinism notes
- The artifact digest should be stable for identical inputs + params + db bundle.
- Query sketch uses canonical k-mers and stable bottom-k selection.

Policy gating
- Downstream policies may require `resolution.status == resolved` for decision grade.

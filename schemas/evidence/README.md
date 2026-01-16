# helix_run_evidence_v1

Purpose: a self-contained record of a single Helix run’s configuration and outcome distribution that downstream systems (VeriBiota/OGN) can verify and archive.

Top-level fields
- `schema`: must equal `helix_run_evidence_v1`.
- `evidence_id`: unique id (`helix-run-<uuid>`).
- `helix_version`: Helix version string.
- `generated_at`: ISO8601 UTC timestamp.
- `run`: summary of the run (id, label, kind, guide_id, target_locus, outcomes count, preset_id, backend, scoring_versions).
- `genome`: id, length, sequence_hash, include_sequence flag, optional sequence when explicitly included.
- `preset`: optional copy of the preset used.
- `outcomes`: list of outcomes with probabilities and annotations.
- `physics`: backend/scoring metadata.
- `checksums`: `payload_sha256` (normalized JSON, sans checksums) and optional `snapshot_sha256` if the original snapshot was provided.

Invariants (intended for VeriBiota checks)
- All `prob` values are >= 0 and sum to ~1.0 (allow small epsilon).
- `frameshift` flags match outcome categories.
- For prime runs, `perfect_prime`, `indel_adjacent`, `rtt_utilization` (if present) should agree with recomputed values from outcomes.

Sequence handling
- `include_sequence=false` (default): `genome.sequence` omitted/null, `sequence_hash` present.
- `include_sequence=true`: `genome.sequence` included alongside `sequence_hash`.

Hashes
- `payload_sha256`: SHA over the evidence payload without the `checksums` block.
- `snapshot_sha256`: SHA of the source snapshot, when provided.

# RunDescriptor v0.1

Canonical, vendor-agnostic run metadata for Omnis/Helix ingestion. JSON schema lives in `run_descriptor.schema.json`.

## Required fields
- `schema_version`: `run_descriptor_v0.1`
- `instrument`: vendor/model/serial/vendor_run_id/data_uri (+ start/complete timestamps)
- `assay`: assay or panel name, read structure/lengths, normalized sample sheet records, barcodes
- `samples`: optional higher-level sample metadata (library/project/subject)
- `data_products`: FASTQ sets (required) plus optional BAM/VCF/QC URIs + checksums
- `routing`: pipeline, reference build, FM index id, Helix project/experiment, priority
- `provenance`: translator id/version, collected_at timestamp, notes

## RunBundle layout (tar.gz)
```
run-<vendor_run_id>-<UTC timestamp>.tar.gz
  descriptor.json        # RunDescriptor
  sample_sheet.raw.csv   # optional original sample sheet
  data/                  # optional embedded FASTQ/BAM/VCF
  reports/               # optional vendor QC outputs
  checksums.sha256       # sha256 <relative_path>
```

## Illumina run folder → RunDescriptor mapping
- Completion markers: `RTAComplete.txt` or `CopyComplete.txt`.
- Run ids: folder name or `RunParameters.xml:RunId`.
- Instrument: `RunInfo.xml:Instrument`, flowcell ID from `Flowcell`.
- Assay/read structure: `Read` entries in `RunInfo.xml` → `read_structure` and `read_lengths`.
- Sample sheet: `SampleSheet.csv` → `assay.sample_sheet.records` with `Sample_ID`, `Sample_Project`, `Description`, `index`, `index2`.
- Data products: FASTQ under `Data/Intensities/BaseCalls` or `Analysis/**/fastq`; attach `lane` from filename (L001) and `sample_id` from Sample_ID.

## BaseSpace / Connect / Ion Torrent notes
- BaseSpace: use REST to enumerate runs and FASTQ datasets; `vendor_run_id = Run.Id`; data URIs are dataset download links or basemount paths.
- Ion Torrent: Torrent Suite plugin posts JSON with run path and FASTQ/BAM/VCF URIs; map directly into `data_products` and `routing` hints.
- Thermo Fisher Connect: Connect Transfer syncs run output to local path; watcher treats it like an Illumina-style folder plus Connect metadata sidecar.

Packaged copy of the schema ships at `src/helix/schema/run_descriptor.schema.json`; keep it in sync with this folder.
For a user-facing walkthrough, see `docs/run_ingest.md`.

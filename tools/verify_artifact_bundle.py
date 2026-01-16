from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


class ArtifactBundleVerifyError(RuntimeError):
    pass


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_streaming(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_relpath(rel: str) -> str:
    token = str(rel or "").replace("\\", "/").strip()
    if not token:
        raise ArtifactBundleVerifyError("entry path is empty")
    if token.startswith("/"):
        raise ArtifactBundleVerifyError(f"entry path is absolute: {rel!r}")
    parts = token.split("/")
    if any(p in {"", ".", ".."} for p in parts):
        raise ArtifactBundleVerifyError(f"entry path is not normalized: {rel!r}")
    return token


@dataclass(frozen=True, slots=True)
class ManifestEntry:
    path: str
    sha256: str
    size: int | None


def _parse_entries(manifest: Mapping[str, Any]) -> tuple[str, list[ManifestEntry]]:
    if isinstance(manifest.get("entries"), list):
        key = "entries"
    elif isinstance(manifest.get("files"), list):
        key = "files"
    else:
        raise ArtifactBundleVerifyError("manifest missing entries/files list")

    raw_entries = manifest.get(key)
    assert isinstance(raw_entries, list)
    entries: list[ManifestEntry] = []
    for raw in raw_entries:
        if not isinstance(raw, Mapping):
            continue
        try:
            rel = _validate_relpath(str(raw.get("path") or ""))
        except ArtifactBundleVerifyError:
            raise
        sha = str(raw.get("sha256") or "").strip().lower()
        if sha.startswith("sha256:"):
            sha = sha[len("sha256:") :]
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ArtifactBundleVerifyError(f"invalid sha256 for {rel!r}: {raw.get('sha256')!r}")
        size: int | None = None
        raw_size = raw.get("size")
        if isinstance(raw_size, int):
            size = raw_size
        entries.append(ManifestEntry(path=rel, sha256=sha, size=size))
    return key, entries


def _bundle_sha256_from_entries(entries: Iterable[ManifestEntry]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda e: e.path):
        digest.update(entry.path.encode("utf-8"))
        digest.update(entry.sha256.encode("utf-8"))
    return digest.hexdigest()


def _load_manifest_from_dir(bundle_dir: Path) -> dict[str, Any]:
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        raise ArtifactBundleVerifyError(f"manifest.json not found in dir: {bundle_dir}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _load_manifest_from_zip(zip_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        try:
            raw = zf.read("manifest.json")
        except KeyError as exc:
            raise ArtifactBundleVerifyError(f"manifest.json not found in zip: {zip_path}") from exc
    return json.loads(raw.decode("utf-8"))


def _read_entry_bytes_from_dir(bundle_dir: Path, rel: str) -> bytes:
    rel_norm = _validate_relpath(rel)
    root = bundle_dir.resolve()
    raw_path = bundle_dir / rel_norm
    if raw_path.is_symlink():
        raise ArtifactBundleVerifyError(f"symlink not allowed: {rel_norm}")
    abs_path = raw_path.resolve()
    if not abs_path.is_relative_to(root):
        raise ArtifactBundleVerifyError(f"entry escapes bundle root: {rel_norm}")
    if not abs_path.exists() or not abs_path.is_file():
        raise ArtifactBundleVerifyError(f"missing entry file: {rel_norm}")
    return abs_path.read_bytes()


def _read_entry_bytes_from_zip(zip_path: Path, rel: str) -> bytes:
    rel_norm = _validate_relpath(rel)
    with zipfile.ZipFile(zip_path, "r") as zf:
        try:
            return zf.read(rel_norm)
        except KeyError as exc:
            raise ArtifactBundleVerifyError(f"missing entry file in zip: {rel_norm}") from exc


def _iter_all_files_dir(root: Path) -> list[str]:
    root = root.resolve()
    rels: list[str] = []
    for base, dirs, files in os.walk(root, followlinks=False):
        base_path = Path(base)
        for name in list(dirs) + list(files):
            p = base_path / name
            if p.is_symlink():
                rel = p.relative_to(root).as_posix()
                raise ArtifactBundleVerifyError(f"symlink not allowed in bundle: {rel}")
        for name in files:
            p = base_path / name
            if p.is_file() and not p.is_symlink():
                rels.append(p.relative_to(root).as_posix())
    rels.sort()
    return rels


def _iter_all_files_zip(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [i.filename for i in zf.infolist() if i.filename and not i.filename.endswith("/")]
    names = [n for n in names if n != ""]  # defensive
    names.sort()
    return names


def verify_artifact_bundle(bundle_path: Path, *, strict: bool = True) -> tuple[bool, tuple[str, ...]]:
    path = Path(bundle_path)
    issues: list[str] = []

    try:
        if path.is_dir():
            manifest = _load_manifest_from_dir(path)
            kind, entries = _parse_entries(manifest)
            expected_paths = {e.path for e in entries}
            expected_paths.add("manifest.json")
            for entry in entries:
                raw = _read_entry_bytes_from_dir(path, entry.path)
                actual_sha = _sha256_hex(raw)
                if actual_sha != entry.sha256:
                    issues.append(f"sha256-mismatch: {entry.path}: expected {entry.sha256} got {actual_sha}")
                if entry.size is not None and entry.size != len(raw):
                    issues.append(f"size-mismatch: {entry.path}: expected {entry.size} got {len(raw)}")
            if strict:
                actual_paths = set(_iter_all_files_dir(path))
                extra = sorted(actual_paths - expected_paths)
                missing = sorted(expected_paths - actual_paths)
                for rel in extra:
                    issues.append(f"extra-file: {rel}")
                for rel in missing:
                    issues.append(f"missing-file: {rel}")

        elif path.is_file() and path.suffix.lower() in {".zip", ".hxs"}:
            manifest = _load_manifest_from_zip(path)
            kind, entries = _parse_entries(manifest)
            expected_paths = {e.path for e in entries}
            expected_paths.add("manifest.json")
            for entry in entries:
                raw = _read_entry_bytes_from_zip(path, entry.path)
                actual_sha = _sha256_hex(raw)
                if actual_sha != entry.sha256:
                    issues.append(f"sha256-mismatch: {entry.path}: expected {entry.sha256} got {actual_sha}")
                if entry.size is not None and entry.size != len(raw):
                    issues.append(f"size-mismatch: {entry.path}: expected {entry.size} got {len(raw)}")
            if strict:
                actual_paths = set(_iter_all_files_zip(path))
                extra = sorted(actual_paths - expected_paths)
                missing = sorted(expected_paths - actual_paths)
                for rel in extra:
                    issues.append(f"extra-file: {rel}")
                for rel in missing:
                    issues.append(f"missing-file: {rel}")
        else:
            raise ArtifactBundleVerifyError(f"unsupported bundle path: {path}")

        # Artifact bundle manifests (helix.artifact_bundle) additionally define bundle_sha256 + manifest_sha256.
        if kind == "entries":
            declared_bundle_sha = str(manifest.get("bundle_sha256") or "").strip().lower()
            computed_bundle_sha = _bundle_sha256_from_entries(entries)
            if declared_bundle_sha and declared_bundle_sha != computed_bundle_sha:
                issues.append(f"bundle-sha256-mismatch: expected {declared_bundle_sha} got {computed_bundle_sha}")
            if not declared_bundle_sha:
                issues.append("bundle-sha256-missing")

            declared_manifest_sha = str(manifest.get("manifest_sha256") or "").strip().lower()
            manifest_copy = dict(manifest)
            manifest_copy.pop("manifest_sha256", None)
            computed_manifest_sha = _sha256_hex(_canonical_json_bytes(manifest_copy))
            if declared_manifest_sha and declared_manifest_sha != computed_manifest_sha:
                issues.append(f"manifest-sha256-mismatch: expected {declared_manifest_sha} got {computed_manifest_sha}")
            if not declared_manifest_sha:
                issues.append("manifest-sha256-missing")

        return (len(issues) == 0), tuple(issues)
    except Exception as exc:
        return False, (f"verify-failed: {exc}",)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Verify a Helix artifact bundle (dir or zip) without Helix.")
    parser.add_argument("bundle", help="Path to bundle directory or .zip/.hxs")
    parser.add_argument("--no-strict", action="store_true", help="Do not fail on extra files outside the manifest.")
    args = parser.parse_args(argv)

    ok, issues = verify_artifact_bundle(Path(args.bundle), strict=not args.no_strict)
    if ok:
        print("OK\tartifact bundle verified")
        return 0
    for issue in issues:
        print(f"FAIL\t{issue}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sha256sums import verify_sha256sums_file
from verify_artifact_bundle import verify_artifact_bundle


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _iter_sha256sums_files(root: Path) -> list[Path]:
    sums = [p for p in root.rglob("SHA256SUMS.txt") if ".git" not in p.parts]
    sums.sort(key=lambda p: p.as_posix())
    return sums


def _read_expected_bundle_sha256(path: Path) -> str:
    token = path.read_text(encoding="utf-8").strip().split()[0].strip().lower()
    if token.startswith("sha256:"):
        token = token[len("sha256:") :]
    return token


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_repo(root: Path) -> tuple[bool, tuple[str, ...]]:
    root = root.resolve()
    issues: list[str] = []

    # 1) Verify all SHA256SUMS.txt files.
    for sums_path in _iter_sha256sums_files(root):
        ok, errs = verify_sha256sums_file(sums_path)
        if not ok:
            for err in errs:
                issues.append(f"{sums_path.relative_to(root).as_posix()}: {err}")

    # 2) Verify any bundle sha256 anchors (convention: *.zip.sha256 contains bundle_sha256).
    for sha_path in sorted(root.glob("bundles/**/*.zip.sha256"), key=lambda p: p.as_posix()):
        zip_path = Path(str(sha_path)[: -len(".sha256")])
        if not zip_path.exists():
            issues.append(f"{sha_path.relative_to(root).as_posix()}: missing zip: {zip_path.name}")
            continue
        expected = _read_expected_bundle_sha256(sha_path)
        ok, bundle_issues = verify_artifact_bundle(zip_path, strict=True)
        if not ok:
            for bi in bundle_issues:
                issues.append(f"{zip_path.relative_to(root).as_posix()}: {bi}")
            continue

        # If it looks like an artifact bundle, also check the published expected bundle_sha256.
        try:
            import zipfile

            with zipfile.ZipFile(zip_path, "r") as zf:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            declared = str(manifest.get("bundle_sha256") or "").strip().lower()
            if declared and expected and declared != expected:
                issues.append(
                    f"{sha_path.relative_to(root).as_posix()}: expected bundle_sha256 {expected} "
                    f"but manifest declares {declared}"
                )
        except Exception as exc:
            issues.append(
                f"{zip_path.relative_to(root).as_posix()}: unable to read manifest for bundle-sha check: {exc}"
            )

    # 3) Verify INDEX.json (if present) matches current file hashes.
    index_path = root / "INDEX.json"
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"INDEX.json: invalid json: {exc}")
            return (len(issues) == 0), tuple(issues)

        if not isinstance(index, dict) or str(index.get("schema") or "") != "helix.public_assets.index.v1":
            issues.append("INDEX.json: unexpected schema")
            return (len(issues) == 0), tuple(issues)

        for entry in index.get("sha256sums") or []:
            if not isinstance(entry, dict):
                continue
            rel = str(entry.get("path") or "")
            exp = str(entry.get("sha256") or "").strip().lower()
            if not rel or not exp:
                continue
            p = root / rel
            if not p.exists():
                issues.append(f"INDEX.json: missing file: {rel}")
                continue
            actual = _sha256_file(p).lower()
            if actual != exp:
                issues.append(f"INDEX.json: sha256 mismatch for {rel}: expected {exp} got {actual}")

        for bundle in index.get("bundles") or []:
            if not isinstance(bundle, dict):
                continue
            rel = str(bundle.get("path") or "")
            exp_zip = str(bundle.get("zip_sha256") or "").strip().lower()
            if not rel or not exp_zip:
                continue
            p = root / rel
            if not p.exists():
                issues.append(f"INDEX.json: missing bundle zip: {rel}")
                continue
            actual_zip = _sha256_file(p).lower()
            if actual_zip != exp_zip:
                issues.append(f"INDEX.json: zip_sha256 mismatch for {rel}: expected {exp_zip} got {actual_zip}")

    return (len(issues) == 0), tuple(issues)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Verify helix-public-assets integrity (hashes + bundle anchors).")
    parser.add_argument("--root", default=str(_repo_root()), help="Repo root (default: inferred).")
    args = parser.parse_args(argv)

    root = Path(args.root)
    ok, issues = verify_repo(root)
    if ok:
        print("OK\trepo verified")
        return 0
    for issue in issues:
        print(f"FAIL\t{issue}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


_SHA256_LINE_RE = re.compile(r"^(?P<sha>[a-fA-F0-9]{64})\s+(?P<path>.+)$")


@dataclass(frozen=True, slots=True)
class Sha256SumsEntry:
    relpath: str
    sha256: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sha256sums(text: str) -> list[Sha256SumsEntry]:
    entries: list[Sha256SumsEntry] = []
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _SHA256_LINE_RE.match(line)
        if not match:
            raise ValueError(f"invalid SHA256SUMS line {lineno}: {raw_line!r}")
        sha = match.group("sha").lower()
        path = match.group("path").strip()
        if path.startswith("*"):
            path = path[1:].strip()
        if path.startswith("./"):
            path = path[2:]
        if not path:
            raise ValueError(f"empty path in SHA256SUMS line {lineno}")
        entries.append(Sha256SumsEntry(relpath=path, sha256=sha))
    return entries


def verify_sha256sums_file(path: Path) -> tuple[bool, list[str]]:
    """Verify a `SHA256SUMS.txt` file.

    Paths are interpreted relative to the sums file's directory.
    """

    sums_path = Path(path)
    base_dir = sums_path.parent
    entries = parse_sha256sums(sums_path.read_text(encoding="utf-8"))

    issues: list[str] = []
    for entry in entries:
        rel = Path(entry.relpath)
        file_path = (base_dir / rel).resolve()
        if not file_path.exists():
            issues.append(f"missing: {entry.relpath}")
            continue
        if file_path.is_symlink():
            issues.append(f"symlink-not-allowed: {entry.relpath}")
            continue
        if not file_path.is_file():
            issues.append(f"not-a-file: {entry.relpath}")
            continue
        try:
            actual = _sha256_file(file_path)
        except Exception as exc:
            issues.append(f"hash-failed: {entry.relpath}: {exc}")
            continue
        if actual.lower() != entry.sha256.lower():
            issues.append(f"sha256-mismatch: {entry.relpath}: expected {entry.sha256} got {actual}")

    return (len(issues) == 0), issues

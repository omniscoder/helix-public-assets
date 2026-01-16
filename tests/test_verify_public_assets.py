from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class TestPublicAssetsVerification(unittest.TestCase):
    def test_verify_artifact_bundle_script(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        bundle = repo_root / "bundles" / "enzyme_program_contract" / "v1.0.0" / "golden_bundle.zip"
        script = repo_root / "tools" / "verify_artifact_bundle.py"
        proc = subprocess.run(
            [sys.executable, str(script), str(bundle)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")

    def test_verify_repo_script(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "tools" / "verify_repo.py"
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")


if __name__ == "__main__":
    unittest.main()


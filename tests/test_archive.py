"""Local tests; no external service calls."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_archive import check_manifest, safe_asset_path, validate
from upload_archive_assets import load_assets

class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))

    def test_manifest(self):
        self.assertEqual(len(check_manifest(self.manifest)), 24)

    def test_metadata_does_not_claim_original_verification(self):
        r = validate(ROOT, metadata_only=True)
        self.assertEqual(r["verified_originals"], 0)
        self.assertEqual(r["semantic_motion_qa"], "NOT_IMPLEMENTED")

    def test_path_guard(self):
        for path in ["/etc/passwd", "../secret", "assets/originals/../../secret",
                     "assets\\originals\\x", "assets/previews/x.png", "assets//originals/x.png"]:
            with self.assertRaises(ValueError):
                safe_asset_path(path)

    def test_duplicate_id(self):
        m = copy.deepcopy(self.manifest)
        m["assets"][1]["id"] = m["assets"][0]["id"]
        with self.assertRaises(ValueError): check_manifest(m)

    def test_bad_hash(self):
        m = copy.deepcopy(self.manifest)
        m["assets"][0]["sha256"] = "not-a-hash"
        with self.assertRaises(ValueError): check_manifest(m)

    def test_count_mismatch(self):
        m = copy.deepcopy(self.manifest)
        m["deduplicated_assets"] = 25
        with self.assertRaises(ValueError): check_manifest(m)

    def test_missing_original_is_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "assets").mkdir()
            (root / "assets/manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
            r = validate(root)
            self.assertEqual(r["status"], "FAIL")
            self.assertEqual(len(r["failures"]), 24)

    def test_missing_archive_member(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.zip"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("assets/manifest.json", json.dumps(self.manifest))
            with self.assertRaises(KeyError): load_assets(path)

    def test_duplicate_zip_member(self):
        import warnings
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(path, "w") as z:
                    z.writestr("assets/manifest.json", "{}")
                    z.writestr("assets/manifest.json", "{}")
            with self.assertRaises(ValueError): load_assets(path)

if __name__ == "__main__": unittest.main()

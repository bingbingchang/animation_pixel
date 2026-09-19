#!/usr/bin/env python3
"""Validate an evidence archive. This is NOT an animation/biomechanics validator."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath


def safe_asset_path(value: str) -> str:
    """Allow only canonical relative original/reference paths, never arbitrary files."""
    if not isinstance(value, str) or "\\" in value or "\x00" in value:
        raise ValueError("Unsafe archive path")
    p = PurePosixPath(value)
    if (p.is_absolute() or ".." in p.parts or str(p) != value
        or len(p.parts) < 3 or p.parts[0] != "assets"
        or p.parts[1] not in {"originals", "references"}):
        raise ValueError(f"Not an allowed asset path: {value!r}")
    return str(p)


def check_manifest(manifest: dict) -> list[dict]:
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("Manifest must contain non-empty assets")
    ids, paths = set(), set()
    for a in assets:
        ident = a["id"]
        path = safe_asset_path(a["path"])
        if ident in ids or path in paths:
            raise ValueError("Duplicate asset id or path")
        ids.add(ident); paths.add(path)
        if not re.fullmatch(r"[GR]\d{2}", ident):
            raise ValueError("Invalid asset id")
        if not re.fullmatch(r"[0-9a-f]{64}", a["sha256"]):
            raise ValueError("Invalid SHA-256")
        if not isinstance(a["bytes"], int) or a["bytes"] <= 0:
            raise ValueError("Invalid byte size")
        if len(a["size"]) != 2 or any(not isinstance(n, int) or n <= 0 for n in a["size"]):
            raise ValueError("Invalid image size")
    if manifest.get("deduplicated_assets") != len(assets):
        raise ValueError("Asset count differs from manifest")
    if manifest.get("raw_bytes") != sum(a["bytes"] for a in assets):
        raise ValueError("Total bytes differ from manifest")
    return assets


def validate(root: Path, metadata_only: bool = False) -> dict:
    manifest = json.loads((root / "assets/manifest.json").read_text(encoding="utf-8"))
    assets = check_manifest(manifest)
    failures, verified = [], []
    if not metadata_only:
        from PIL import Image
        for a in assets:
            p = root / a["path"]
            if not p.is_file():
                failures.append({"id": a["id"], "reason": "missing_original"}); continue
            if root.resolve() not in p.resolve().parents:
                failures.append({"id": a["id"], "reason": "path_escaped_root"}); continue
            raw = p.read_bytes()
            if len(raw) != a["bytes"] or hashlib.sha256(raw).hexdigest() != a["sha256"]:
                failures.append({"id": a["id"], "reason": "byte_or_hash_mismatch"}); continue
            try:
                with Image.open(p) as im:
                    observed = (list(im.size), im.mode, getattr(im, "n_frames", 1))
                    expected = (a["size"], a["mode"], a["file_frame_count"])
                    if observed != expected:
                        failures.append({"id": a["id"], "reason": "image_metadata_mismatch"}); continue
                    alpha = list(im.convert("RGBA").getchannel("A").getextrema())
                    if alpha != a["alpha_min_max"]:
                        failures.append({"id": a["id"], "reason": "alpha_mismatch"}); continue
            except OSError as exc:
                failures.append({"id": a["id"], "reason": str(exc)}); continue
            verified.append(a["id"])
    return {
        "scope": "metadata_only" if metadata_only else "original_file_integrity",
        "status": "FAIL" if failures else "PASS",
        "metadata_assets": len(assets),
        "verified_originals": len(verified),
        "failures": failures,
        "semantic_motion_qa": "NOT_IMPLEMENTED",
        "game_import_qa": "NOT_RUN",
        "note": "PASS means only the stated scope passed; no head/foot/weapon/animation approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--metadata-only", action="store_true")
    group.add_argument("--require-originals", action="store_true")
    args = parser.parse_args()
    try:
        report = validate(args.root, args.metadata_only)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return int(report["status"] != "PASS")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Archive validation failed: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

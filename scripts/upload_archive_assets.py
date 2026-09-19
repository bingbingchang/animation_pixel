#!/usr/bin/env python3
"""Upload allowlisted original assets to an existing branch using authenticated gh.

Default/dry-run validates only local ZIP bytes. --execute explicitly permits
GitHub writes. No image-generation API, credential files, or shell evaluation.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote
from validate_archive import check_manifest

MAX_FILE = 30 * 1024 * 1024
MAX_TOTAL = 250 * 1024 * 1024


def load_assets(archive: Path) -> tuple[dict, list[tuple[dict, bytes]]]:
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entries are not accepted")
        # Canonical flat root; no extraction takes place.
        info = zf.getinfo("assets/manifest.json")
        if info.file_size > 2 * 1024 * 1024:
            raise ValueError("Manifest too large")
        manifest = json.loads(zf.read(info))
        assets = check_manifest(manifest)
        if sum(a["bytes"] for a in assets) > MAX_TOTAL:
            raise ValueError("Total assets exceed safety limit")
        loaded = []
        for a in assets:
            entry = zf.getinfo(a["path"])
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError("ZIP symlinks are not accepted")
            if entry.file_size != a["bytes"] or entry.file_size > MAX_FILE:
                raise ValueError(f"Unsafe file size: {a['id']}")
            raw = zf.read(entry)
            if hashlib.sha256(raw).hexdigest() != a["sha256"]:
                raise ValueError(f"Hash mismatch: {a['id']}")
            loaded.append((a, raw))
        return manifest, loaded


def gh_api(endpoint: str, method: str = "GET", body: dict | None = None):
    args = ["gh", "api", "--hostname", "github.com", "--method", method, endpoint]
    payload = None
    if body is not None:
        args += ["--input", "-"]
        payload = json.dumps(body).encode("utf-8")
    result = subprocess.run(args, input=payload, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        # Do not emit arbitrary stderr, which could contain local credential details.
        raise RuntimeError(f"gh api {method} {endpoint} failed (code {result.returncode})")
    return json.loads(result.stdout) if result.stdout else None


def execute(repo: str, branch: str, manifest: dict, assets: list[tuple[dict, bytes]]) -> str:
    base = f"repos/{repo}"
    refpath = f"{base}/git/ref/heads/{quote(branch, safe='/')}"
    head = gh_api(refpath)["object"]["sha"]
    base_tree = gh_api(f"{base}/git/commits/{head}")["tree"]["sha"]
    listing = gh_api(f"{base}/git/trees/{base_tree}?recursive=1")
    if listing.get("truncated"):
        raise RuntimeError("Base tree truncated; cannot safely inspect existing assets")
    tree = []
    for a, raw in assets:
        # Prevent accidental replacement of a pre-existing different original.
        existing = next((i for i in listing["tree"] if i["path"] == a["path"]), None)
        git_blob_sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if existing and existing["sha"] != git_blob_sha:
            raise RuntimeError(f"Refusing to overwrite different existing asset {a['id']}")
        sha = existing["sha"] if existing else gh_api(f"{base}/git/blobs", "POST", {
            "content": base64.b64encode(raw).decode("ascii"), "encoding": "base64"
        })["sha"]
        if sha != git_blob_sha:
            raise RuntimeError(f"Remote blob hash differs: {a['id']}")
        tree.append({"path": a["path"], "mode": "100644", "type": "blob", "sha": sha})
        print(f"Prepared {a['id']}: {a['bytes']} bytes")
    # Write a receipt, not the manifest: do not overwrite newer annotations.
    receipt = {"schema_version": "1.0", "repository": repo, "branch": branch,
        "base_commit": head, "uploaded_assets": [
            {"id": a["id"], "path": a["path"], "sha256": a["sha256"], "bytes": a["bytes"]}
            for a, _ in assets],
        "verification": "local_hashes_checked; remote_content_addressed_blobs_created; post_update_check_logged_to_terminal",
        "semantic_motion_qa": "NOT_IMPLEMENTED"}
    tree.append({"path": "reports/originals-upload-receipt.json", "mode": "100644",
                 "type": "blob", "content": json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"})
    new_tree = gh_api(f"{base}/git/trees", "POST", {"base_tree": base_tree, "tree": tree})["sha"]
    commit = gh_api(f"{base}/git/commits", "POST", {
        "message": "archive: upload original animation evidence assets with checksums",
        "tree": new_tree, "parents": [head]
    })["sha"]
    if gh_api(refpath)["object"]["sha"] != head:
        raise RuntimeError("Branch changed during upload; refusing to update. Rerun after reviewing changes.")
    gh_api(f"{base}/git/refs/heads/{quote(branch, safe='/')}", "PATCH", {"sha": commit, "force": False})
    remote_tree = gh_api(f"{base}/git/trees/{new_tree}?recursive=1")
    remote = {i["path"]: i["sha"] for i in remote_tree["tree"]}
    if remote_tree.get("truncated") or any(remote.get(i["path"]) != i["sha"] for i in tree if "sha" in i):
        raise RuntimeError("Remote tree verification failed; inspect the new commit before claiming success")
    print(f"Verified {len(assets)} original files at commit {commit}")
    return commit


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--repo", default="bingbingchang/animation_pixel")
    p.add_argument("--branch", default="archive/2026-09-19-motion-cases")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = p.parse_args()
    try:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
            raise ValueError("Invalid owner/repository")
        if not re.fullmatch(r"[A-Za-z0-9_/-]+", args.branch):
            raise ValueError("Invalid branch name")
        manifest, assets = load_assets(args.archive)
        print(f"Local bytes verified: {len(assets)} files; {sum(len(b) for _, b in assets)} bytes")
        if not args.execute:
            print("DRY RUN: no network request, no GitHub writes. Use --execute to upload.")
            return 0
        if shutil.which("gh") is None:
            raise RuntimeError("GitHub CLI (gh) is not installed. Authenticate gh on your own computer first.")
        execute(args.repo, args.branch, manifest, assets)
        return 0
    except (OSError, KeyError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"Upload stopped: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

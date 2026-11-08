#!/usr/bin/env python3
"""Pack the formal run's Volume evidence into one tarball (single transfer).

The 8,300 small files cannot be downloaded efficiently over the flaky API
proxy, and walking the volume FUSE mount inside a container is slow.  This App
therefore lists/reads the volume through the Volume API (internal RPCs) and
writes one tarball back to the volume, which the Lead downloads as a single
file.
"""
from __future__ import annotations

import hashlib
import io
import json
import tarfile
import time

import modal

VOLUME_NAME = "tii-v6-scalability"
PREFIX = "scalability_v6_formal"
TOPS = ("protocol", "run_metadata", "raw", "completion_ledger", "hashes",
        "metrics", "logs")
app = modal.App("tii-v6-pack")
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=False)
image = modal.Image.debian_slim(python_version="3.13")


@app.function(image=image, volumes={"/vol": volume}, cpu=1.0, memory=2048,
              timeout=1800, retries=0, single_use_containers=True)
def pack(prefix: str = PREFIX) -> dict:
    from modal.types import FileEntryType

    vol = modal.Volume.from_name(VOLUME_NAME)
    root = f"/{prefix.strip('/')}"
    export_dir = f"/vol/{prefix.strip('/')}/exports"
    import os
    os.makedirs(export_dir, exist_ok=True)
    out_path = os.path.join(export_dir, f"{prefix.strip('/')}_evidence.tar.gz")
    digest = hashlib.sha256()
    files = 0
    started = time.time()
    with open(out_path, "wb") as raw:
        class HashWriter(io.RawIOBase):
            def writable(self):
                return True
            def write(self, b):
                digest.update(b)
                return raw.write(b)
        with tarfile.open(fileobj=HashWriter(), mode="w|gz", compresslevel=6) as tar:
            for top in TOPS:
                try:
                    entries = vol.listdir(f"{root}/{top}", recursive=True)
                except Exception:  # noqa: BLE001
                    continue
                for entry in sorted(entries, key=lambda e: str(e.path)):
                    if int(getattr(entry, "type", 0)) != int(FileEntryType.FILE):
                        continue
                    remote = str(entry.path)
                    data = b"".join(vol.read_file(remote))
                    rel = remote.lstrip("/")
                    if rel.startswith(f"{prefix.strip('/')}/"):
                        rel = rel[len(prefix.strip('/')) + 1:]
                    tarinfo = tarfile.TarInfo(rel)
                    tarinfo.size = len(data)
                    tarinfo.mtime = int(time.time())
                    tar.addfile(tarinfo, io.BytesIO(data))
                    files += 1
    volume.commit()
    return {"path": out_path, "bytes": os.path.getsize(out_path),
            "sha256": digest.hexdigest(), "files": files,
            "elapsed_s": round(time.time() - started, 2)}


@app.local_entrypoint()
def main(prefix: str = PREFIX):
    print(json.dumps(pack.remote(prefix), indent=2, sort_keys=True))

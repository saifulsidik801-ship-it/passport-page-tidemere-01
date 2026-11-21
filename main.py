#!/usr/bin/env python3
"""Passport Page of a Country That Isn't There -- entry program.

Writes /output/entry.png: an invented passport spread for the Republic
of Tidemere, a tidal archipelago whose only land link is a causeway
passable at low water. The image is pre-rendered (drawn with Pillow by
render.py in the builder's session) and shipped beside this script;
this program copies it to /output, deterministically and
byte-identically.

Standard library only: hashlib, os, shutil and sys. No third-party
packages are needed or used, and no network is touched.
"""
import hashlib
import os
import shutil
import sys


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Verify the copy: the output must be a byte-identical copy of the
    # source. Size alone cannot prove that, so compare SHA-256 digests
    # as well. A zero-byte, size-mismatched, or hash-mismatched output
    # means the copy failed (e.g. disk full) and must not be silently
    # accepted.
    src_size = os.path.getsize(src)
    dst_size = os.path.getsize(dst)
    src_hash = sha256_of(src)
    dst_hash = sha256_of(dst)
    if dst_size == 0 or dst_size != src_size or dst_hash != src_hash:
        print(f"error: copy verification failed: {src} ({src_size} bytes, "
              f"sha256 {src_hash}) -> {dst} ({dst_size} bytes, "
              f"sha256 {dst_hash})", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({dst_size} bytes, sha256 {dst_hash})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

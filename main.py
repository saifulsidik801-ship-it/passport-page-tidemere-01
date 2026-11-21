#!/usr/bin/env python3
"""Passport Page of a Country That Isn't There -- entry program.

Writes /output/entry.png: an invented passport spread for the Republic
of Tidemere, a tidal archipelago whose only land link is a causeway
passable at low water. The image is pre-rendered (drawn with Pillow by
render.py in the builder's session) and shipped beside this script;
this program copies it to /output, deterministically and
byte-identically.

Standard library only: os, shutil and sys. No third-party packages are
needed or used, and no network is touched.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Verify the copy: the output must be a byte-identical copy of the
    # source. A zero-byte or size-mismatched output means the copy
    # failed (e.g. disk full) and must not be silently accepted.
    src_size = os.path.getsize(src)
    dst_size = os.path.getsize(dst)
    if dst_size == 0 or dst_size != src_size:
        print(f"error: copy verification failed: {src} ({src_size} bytes) "
              f"-> {dst} ({dst_size} bytes)", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({dst_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

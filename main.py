"""Write the news-image-20261117 entry image to the output directory.

The entry image - "ONE DAY - ONE ORBIT", a poster that sums up the
world news of Tuesday 17 November 2026 in a single picture - ships in
this repository as entry.png. This program copies it to
/output/entry.png (or to $MAKEFUN_OUTPUT_DIR when that is set) byte
for byte. Standard library only, no network, fully deterministic:
every run writes exactly the same bytes.
"""
import os
import shutil
from pathlib import Path

ASSET_NAME = "entry.png"
OUTPUT_NAME = "entry.png"


def main() -> None:
    here = Path(__file__).resolve().parent
    asset = here / ASSET_NAME
    if not asset.is_file():
        raise SystemExit(f"asset missing from repository: {asset}")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / OUTPUT_NAME
    # copyfile moves the bytes verbatim: no decode, no re-encode, so the
    # output is identical to the shipped asset on every run.
    shutil.copyfile(asset, target)
    if target.read_bytes() != asset.read_bytes():
        raise SystemExit("output does not match the shipped asset byte for byte")


if __name__ == "__main__":
    main()

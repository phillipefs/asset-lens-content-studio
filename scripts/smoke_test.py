"""Run two end-to-end render and compliance smoke tests."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "asset-lens-post-studio"
RUNNER = SKILL / "scripts" / "run.py"
VERIFIER = SKILL / "scripts" / "verify_output.py"
SMOKE_ROOT = ROOT / ".tmp" / "smoke"
CASES = ("concept", "screenshot")


def execute(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    if SMOKE_ROOT.exists():
        shutil.rmtree(SMOKE_ROOT)
    SMOKE_ROOT.mkdir(parents=True)

    summary: dict[str, dict[str, object]] = {}
    for case in CASES:
        fixture = ROOT / "tests" / "fixtures" / case
        config_path = fixture / "render.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        output_dir = ROOT / config["output_dir"]

        execute([sys.executable, str(RUNNER), "--config", str(config_path)])
        shutil.copy2(fixture / "copy.md", output_dir / "copy.md")
        shutil.copy2(config_path, output_dir / "render.json")

        png_path = output_dir / config.get("filename", "post.png")
        copy_path = output_dir / "copy.md"
        copied_config = output_dir / "render.json"
        execute([
            sys.executable,
            str(VERIFIER),
            str(png_path),
            str(copy_path),
            str(copied_config),
        ])

        with Image.open(png_path) as image:
            if image.size != (1080, 1350):
                raise AssertionError(f"Unexpected smoke image dimensions for {case}: {image.size}")
            summary[case] = {
                "png": str(png_path.relative_to(ROOT)),
                "size": list(image.size),
            }

    print(json.dumps({"status": "ok", "cases": summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Renderiza posts do Asset Lens: config JSON -> HTML premium -> PNG final.

Pipeline: build_html.py monta um HTML autossuficiente (fontes/logo/screenshot
como data URI); um Chromium local (Chrome ou Edge) captura em 2x; Pillow
reduz para o tamanho final com LANCZOS. A copy é escrita pelo agente, não aqui.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))
import build_html  # noqa: E402


def ensure_pillow() -> bool:
    """Garante Pillow no interpretador atual ou re-executa via venv local."""
    try:
        import PIL  # noqa: F401

        return True
    except Exception:
        pass

    if os.environ.get("ASSET_LENS_NO_BOOTSTRAP"):
        return False

    runtime = SKILL_DIR / ".runtime" / "venv"
    python_bin = runtime / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    pip_bin = runtime / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")

    try:
        if not python_bin.exists():
            runtime.parent.mkdir(parents=True, exist_ok=True)
            print("Preparando runtime local da skill...", flush=True)
            venv.EnvBuilder(with_pip=True, clear=False).create(runtime)
        check = subprocess.run([str(python_bin), "-c", "import PIL"], capture_output=True)
        if check.returncode != 0:
            print("Instalando Pillow no runtime local...", flush=True)
            subprocess.run([str(pip_bin), "install", "Pillow>=10.0"], check=True)
        env = dict(os.environ, ASSET_LENS_NO_BOOTSTRAP="1")
        result = subprocess.run([str(python_bin), *sys.argv], env=env)
        raise SystemExit(result.returncode)
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - defensivo
        print(f"Aviso: bootstrap do Pillow falhou ({exc}); seguindo sem downscale.", flush=True)
        return False


def find_browser() -> Path:
    override = os.environ.get("ASSET_LENS_BROWSER")
    if override and Path(override).exists():
        return Path(override)

    candidates = [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return Path(candidate)
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(name)
        if found:
            return Path(found)
    raise RuntimeError(
        "Nenhum Chrome/Edge encontrado para o render headless. "
        "Instale um deles ou defina ASSET_LENS_BROWSER com o caminho do executável."
    )


def capture(browser: Path, html_path: Path, out_png: Path, width: int, height: int, scale: int = 2) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--disable-extensions",
        "--no-first-run",
        f"--force-device-scale-factor={scale}",
        f"--window-size={width},{height}",
        "--default-background-color=FF010409",
        "--virtual-time-budget=4000",
        f"--screenshot={out_png}",
        html_path.resolve().as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if not out_png.exists():
        detail = (result.stderr or result.stdout or "").strip()[-800:]
        raise RuntimeError(f"Screenshot headless falhou para {html_path.name}: {detail}")


def downscale(png_path: Path, width: int, height: int) -> None:
    from PIL import Image

    with Image.open(png_path) as img:
        if img.size == (width, height):
            return
        resized = img.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    resized.save(png_path, optimize=True)


def find_studio_root(start: Path) -> Path | None:
    """Encontra a fronteira do estúdio sem depender de um repositório Git."""
    current = start.expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "studio.config.json").is_file():
            return candidate
    return None


def resolve_project_root(spec: dict, config_path: Path) -> Path:
    configured = spec.get("project_root")
    if configured:
        root = Path(configured).expanduser()
        if not root.is_absolute():
            root = config_path.parent / root
        return root.resolve()
    config_root = find_studio_root(config_path.parent)
    if config_root:
        return config_root
    for env_name in ("ASSET_LENS_PROJECT_ROOT", "CLAUDE_PROJECT_DIR", "CLAUDE_CODE_PROJECT_DIR"):
        value = os.environ.get(env_name)
        if value and Path(value).expanduser().exists():
            return Path(value).expanduser().resolve()
    studio_root = find_studio_root(Path.cwd())
    if studio_root:
        return studio_root
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=config_path.parent, capture_output=True, text=True, check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).resolve()
    except Exception:
        pass
    return Path.cwd().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Renderiza posts premium do Asset Lens.")
    parser.add_argument("--config", required=True, help="Caminho do JSON de configuração")
    parser.add_argument("--html-only", action="store_true", help="Só gera o HTML (depuração)")
    args = parser.parse_args()

    has_pillow = ensure_pillow()

    config_path = Path(args.config).resolve()
    spec = json.loads(config_path.read_text(encoding="utf-8"))

    project_root = resolve_project_root(spec, config_path)
    default_dir = f"instagram/{_dt.date.today():%Y-%m-%d}-post"
    output_dir = Path(spec.get("output_dir", default_dir))
    if not output_dir.is_absolute():
        output_dir = (project_root / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if spec.get("mode", "post") == "carousel":
        common = {k: v for k, v in spec.items() if k not in {"slides", "mode", "base_name"}}
        slides = spec.get("slides") or []
        jobs = []
        for idx, slide in enumerate(slides, start=1):
            merged = {**common, **slide}
            merged.setdefault("slide_number", f"{idx}/{len(slides)}")
            jobs.append((merged, slide.get("filename", f"slide-{idx:02d}.png"), f"render-{idx:02d}.html"))
    else:
        jobs = [(spec, spec.get("filename", "post.png"), "render.html")]

    browser = None if args.html_only else find_browser()

    generated: list[Path] = []
    warnings: list[str] = []
    for slide_spec, filename, html_name in jobs:
        fmt = build_html.normalize_spec(slide_spec).get("format", "feed_4x5")
        width, height = build_html.DIMENSIONS.get(fmt, build_html.DIMENSIONS["feed_4x5"])

        html_path = output_dir / html_name
        html_path.write_text(build_html.build_slide_html(slide_spec), encoding="utf-8")
        if args.html_only:
            generated.append(html_path)
            continue

        png_path = output_dir / filename
        capture(browser, html_path, png_path, width, height)
        if has_pillow:
            downscale(png_path, width, height)
        else:
            warnings.append(
                f"{filename}: entregue em 2x ({width * 2}x{height * 2}) — Pillow indisponível para downscale."
            )
        generated.append(png_path)

    print(json.dumps({
        "status": "ok",
        "engine": "chromium-headless",
        "browser": str(browser) if browser else None,
        "files": [str(p.resolve()) for p in generated],
        "warnings": warnings,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

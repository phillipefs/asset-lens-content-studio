"""Validate the Asset Lens Content Studio structure and agent integrations."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency error path
    raise SystemExit(
        "PyYAML is required. Run: python -m pip install -r requirements-dev.txt"
    ) from exc

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - dependency error path
    raise SystemExit(
        "Pillow is required. Run: python -m pip install -r requirements-dev.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / ".agents" / "skills" / "asset-lens-post-studio"
ADAPTER = ROOT / ".claude" / "skills" / "asset-lens-post-studio"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

failures: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"Invalid JSON: {path.relative_to(ROOT)} ({exc})")
        return {}
    check(isinstance(value, dict), f"JSON root must be an object: {path.relative_to(ROOT)}")
    return value if isinstance(value, dict) else {}


def load_yaml(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"Invalid YAML: {path.relative_to(ROOT)} ({exc})")
        return {}
    check(isinstance(value, dict), f"YAML root must be a mapping: {path.relative_to(ROOT)}")
    return value if isinstance(value, dict) else {}


def load_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    check(len(parts) == 3 and not parts[0].strip(), f"Missing YAML frontmatter: {path.relative_to(ROOT)}")
    if len(parts) != 3:
        return {}, text
    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except Exception as exc:
        failures.append(f"Invalid frontmatter: {path.relative_to(ROOT)} ({exc})")
        return {}, parts[2]
    check(isinstance(metadata, dict), f"Frontmatter must be a mapping: {path.relative_to(ROOT)}")
    return metadata if isinstance(metadata, dict) else {}, parts[2]


def validate_skill(path: Path, canonical: bool) -> None:
    skill_file = path / "SKILL.md"
    check(skill_file.is_file(), f"Missing skill file: {skill_file.relative_to(ROOT)}")
    if not skill_file.is_file():
        return
    metadata, _body = load_frontmatter(skill_file)
    name = str(metadata.get("name", ""))
    description = str(metadata.get("description", ""))
    check(name == path.name, f"Skill name must match directory: {path.relative_to(ROOT)}")
    check(bool(NAME_PATTERN.fullmatch(name)), f"Invalid skill name: {name!r}")
    check(1 <= len(description) <= 1024, f"Skill description length invalid: {path.relative_to(ROOT)}")
    if canonical:
        compatibility = str(metadata.get("compatibility", ""))
        check(1 <= len(compatibility) <= 500, "Canonical compatibility must be 1-500 characters")
        check(isinstance(metadata.get("allowed-tools"), str), "Canonical allowed-tools must be a string")
        check(len(skill_file.read_text(encoding="utf-8").splitlines()) < 500, "Canonical SKILL.md must stay under 500 lines")


def validate_required_files() -> None:
    required = [
        ROOT / "AGENTS.md",
        ROOT / "CLAUDE.md",
        ROOT / "INSTRUCTION_USE.md",
        ROOT / "studio.config.json",
        CANONICAL / "SKILL.md",
        CANONICAL / "brand_guide.md",
        CANONICAL / "QUALITY_STANDARD.md",
        CANONICAL / "scripts" / "build_html.py",
        CANONICAL / "scripts" / "run.py",
        CANONICAL / "scripts" / "verify_output.py",
        CANONICAL / "references" / "product-brief.md",
        CANONICAL / "references" / "feature-catalog.md",
        CANONICAL / "references" / "compliance.md",
        CANONICAL / "references" / "messaging.md",
        CANONICAL / "references" / "current-snapshot.md",
        CANONICAL / "references" / "brand" / "logo_official.png",
        CANONICAL / "agents" / "openai.yaml",
        ADAPTER / "SKILL.md",
        ROOT / "inputs" / "screenshots" / "2026-07-20-zonas-app.png",
        ROOT / "inputs" / "screenshots" / "2026-07-20-zonas-app.md",
    ]
    for path in required:
        check(path.is_file(), f"Missing required file: {path.relative_to(ROOT)}")


def validate_visual_assets() -> None:
    expected_examples = {
        "benchmark_post_01.png",
        "carrossel-aprovado-01-capa.png",
        "carrossel-aprovado-02-drawdown.png",
        "carrossel-aprovado-03-setores.png",
        "carrossel-aprovado-04-ciclos.png",
        "carrossel-aprovado-05-ocorrencias.png",
        "post-aprovado-drawdown.png",
    }
    examples_dir = CANONICAL / "references" / "approved_examples"
    actual_examples = {path.name for path in examples_dir.glob("*.png")}
    check(expected_examples.issubset(actual_examples), "Approved example set is incomplete")

    expected_fonts = {
        "Inter-Variable.ttf",
        "Poppins-Bold.ttf",
        "Poppins-Medium.ttf",
        "Poppins-SemiBold.ttf",
    }
    fonts_dir = CANONICAL / "assets" / "fonts"
    actual_fonts = {path.name for path in fonts_dir.glob("*.ttf")}
    check(expected_fonts.issubset(actual_fonts), "Required font set is incomplete")

    logo_path = CANONICAL / "references" / "brand" / "logo_official.png"
    if logo_path.is_file():
        with Image.open(logo_path) as logo:
            check("A" in logo.getbands(), "Official logo must preserve an alpha channel")

    screenshot_path = ROOT / "inputs" / "screenshots" / "2026-07-20-zonas-app.png"
    if screenshot_path.is_file():
        with Image.open(screenshot_path) as screenshot:
            check(screenshot.width >= 600 and screenshot.height >= 300, "Seed screenshot is unexpectedly small")


def validate_agent_wiring() -> None:
    validate_skill(CANONICAL, canonical=True)
    validate_skill(ADAPTER, canonical=False)

    adapter_files = [path.relative_to(ADAPTER).as_posix() for path in ADAPTER.rglob("*") if path.is_file()]
    check(adapter_files == ["SKILL.md"], "Claude adapter must contain only SKILL.md")

    adapter_text = (ADAPTER / "SKILL.md").read_text(encoding="utf-8")
    target = "../../../.agents/skills/asset-lens-post-studio/SKILL.md"
    check(target in adapter_text, "Claude adapter does not reference the canonical skill")

    settings = load_json(ROOT / ".vscode" / "settings.json")
    locations = settings.get("chat.agentSkillsLocations", {})
    check(locations.get(".agents/skills") is True, "Copilot must enable .agents/skills")
    check(locations.get(".claude/skills") is False, "Copilot must disable the Claude project adapter")
    check(settings.get("chat.useAgentsMdFile") is True, "Copilot must load AGENTS.md")
    check(settings.get("chat.useClaudeMdFile") is False, "Copilot must not duplicate CLAUDE.md")

    claude_text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    check("@AGENTS.md" in claude_text, "CLAUDE.md must import AGENTS.md")

    openai = load_yaml(CANONICAL / "agents" / "openai.yaml")
    check(bool(openai.get("interface", {}).get("display_name")), "Codex openai.yaml needs a display name")
    for key in ("icon_small", "icon_large"):
        icon = str(openai.get("interface", {}).get(key, ""))
        check(icon.startswith("./"), f"Codex {key} must be relative to the skill root")
        check((CANONICAL / icon.removeprefix("./")).is_file(), f"Codex {key} target does not exist")


def validate_root_and_ignores() -> None:
    config = load_json(ROOT / "studio.config.json")
    check(config.get("canonical_skill") == ".agents/skills/asset-lens-post-studio", "Canonical skill path mismatch")
    check(config.get("claude_adapter") == ".claude/skills/asset-lens-post-studio", "Claude adapter path mismatch")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in (
        "instagram/**/post.png",
        "instagram/**/slide-*.png",
        "instagram/**/render.html",
        "instagram/**/render-*.html",
    ):
        check(pattern in gitignore, f"Missing generated-artifact ignore rule: {pattern}")

    run_path = CANONICAL / "scripts" / "run.py"
    spec = importlib.util.spec_from_file_location("asset_lens_studio_run", run_path)
    check(spec is not None and spec.loader is not None, "Could not load run.py for root test")
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        resolved = module.resolve_project_root({}, ROOT / "tests" / "fixtures" / "concept" / "render.json")
        check(resolved == ROOT, f"Renderer resolved wrong project root: {resolved}")


def validate_usage_manual() -> None:
    manual_path = ROOT / "INSTRUCTION_USE.md"
    if not manual_path.is_file():
        return
    manual = manual_path.read_text(encoding="utf-8")
    json_blocks = re.findall(r"```json\s*(.*?)```", manual, flags=re.DOTALL)
    check(bool(json_blocks), "Usage manual must contain JSON examples")
    for index, block in enumerate(json_blocks, start=1):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid JSON example #{index} in INSTRUCTION_USE.md ({exc})")

    for visual in ("screenshot", "steps", "stats", "sectors", "drawdown", "cycles", "none"):
        check(f"`{visual}`" in manual, f"Usage manual does not cover visual type: {visual}")
    for format_name in ("feed_4x5", "square", "story_9x16"):
        check(format_name in manual, f"Usage manual does not cover format: {format_name}")
    check(
        "Conteúdo informacional. Não é recomendação de investimento." in manual,
        "Usage manual must contain the exact disclaimer",
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("INSTRUCTION_USE.md" in readme, "README.md must link to the usage manual")


def main() -> int:
    validate_required_files()
    validate_visual_assets()
    validate_agent_wiring()
    validate_root_and_ignores()
    validate_usage_manual()

    if failures:
        print("Studio validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(f"Studio validation OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
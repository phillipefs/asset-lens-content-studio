"""Constrói o HTML final de um post do Asset Lens a partir de um config JSON.

O HTML é autossuficiente: fontes, logo e screenshots entram como data URI,
portanto o render headless não depende de rede. A captura é feita por run.py.
"""
from __future__ import annotations

import base64
import html
import json
import math
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
FONTS_DIR = SKILL_DIR / "assets" / "fonts"
DEFAULT_LOGO = SKILL_DIR / "references" / "brand" / "logo_official.png"

PALETTE = {
    "bg_top": "#020810",
    "bg_bottom": "#010409",
    "surface": "#07111D",
    "surface_2": "#0A1828",
    "surface_3": "#0E1F31",
    "border": "#125676",
    "cyan": "#22D8F4",
    "teal": "#15E8D1",
    "blue": "#41B4FF",
    "green": "#39DB9B",
    "white": "#F4F7FB",
    "text_2": "#BFCAD8",
    "text_3": "#8FA0B4",
    "yellow": "#FFBF57",
    "red": "#FF667B",
}

DIMENSIONS = {
    "feed_4x5": (1080, 1350),
    "square": (1080, 1080),
    "story_9x16": (1080, 1920),
}

DEFAULT_DISCLAIMER = "Conteúdo informacional. Não é recomendação de investimento."

# Ícones estilo stroke (viewBox 24), coerentes com as referências aprovadas.
ICON_PATHS = {
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2"/>',
    "shield": '<path d="M12 2.5 20 6v6c0 4.8-3.3 8.2-8 9.5C7.3 20.2 4 16.8 4 12V6l8-3.5z"/>',
    "shield-check": '<path d="M12 2.5 20 6v6c0 4.8-3.3 8.2-8 9.5C7.3 20.2 4 16.8 4 12V6l8-3.5z"/><polyline points="8.5 12 11 14.5 15.5 9.5"/>',
    "trend-down": '<polyline points="2 6.5 9 13.5 13.5 9 22 17.5"/><polyline points="16 17.5 22 17.5 22 11.5"/>',
    "trend-up": '<polyline points="2 17.5 9 10.5 13.5 15 22 6.5"/><polyline points="16 6.5 22 6.5 22 12.5"/>',
    "cycle": '<polyline points="22 3.5 22 9.5 16 9.5"/><polyline points="2 20.5 2 14.5 8 14.5"/><path d="M4 9.5a8.6 8.6 0 0 1 14.2-3.2L22 9.5"/><path d="M2 14.5l3.8 3.2A8.6 8.6 0 0 0 20 14.5"/>',
    "pie": '<path d="M21.2 15.9A10 10 0 1 1 8.1 2.8"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
    "bars": '<line x1="6" y1="20" x2="6" y2="11"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="18" y1="20" x2="18" y2="14"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><polyline points="12 6.5 12 12 15.8 14"/>',
    "layers": '<polygon points="12 2.5 22 7.5 12 12.5 2 7.5"/><polyline points="2 12.5 12 17.5 22 12.5"/><polyline points="2 17 12 22 22 17"/>',
    "target": '<circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="12" r="1.6"/>',
    "chevron": '<polyline points="9 5 16 12 9 19"/>',
    "grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.4"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.4"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.4"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.4"/>',
    "pin": '<path d="M20 10c0 6.4-8 12-8 12s-8-5.6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="2.8"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4.5 20.5a7.5 7.5 0 0 1 15 0"/>',
    "zoom": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2"/><line x1="8.2" y1="11" x2="13.8" y2="11"/><line x1="11" y1="8.2" x2="11" y2="13.8"/>',
}

CHIP_ICON_KEYWORDS = [
    (("risco", "risk", "proteç"), "shield-check"),
    (("queda", "drawdown", "máxima", "maxima"), "trend-down"),
    (("recupera", "retomada"), "trend-up"),
    (("ciclo", "ocorrênc", "ocorrenc", "comportamento"), "cycle"),
    (("setor", "setorial", "grupo"), "pie"),
    (("históric", "historic", "tempo", "prazo", "período", "periodo"), "clock"),
    (("compar", "métric", "metric", "média", "media"), "bars"),
    (("leitura", "análise", "analise", "visão", "visao"), "search"),
    (("faixa", "quantitativ", "percentil"), "target"),
    (("contexto", "camada", "agregad"), "layers"),
    (("individual", "ativo"), "user"),
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def esc(text: Any) -> str:
    return html.escape(str(text), quote=True)


def color_value(name: str | None, fallback: str = "white") -> str:
    if not name:
        name = fallback
    name = str(name).strip()
    if name.startswith("#"):
        return name
    return PALETTE.get(name, PALETTE[fallback])


def data_uri(path: Path, mime: str) -> str:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def font_face_css() -> str:
    """Embute Poppins (títulos) e Inter (texto). Fallback: Segoe UI local."""
    faces = []
    specs = [
        ("Poppins", "Poppins-Medium.ttf", 500, "truetype"),
        ("Poppins", "Poppins-SemiBold.ttf", 600, "truetype"),
        ("Poppins", "Poppins-Bold.ttf", 700, "truetype"),
    ]
    for family, filename, weight, fmt in specs:
        path = FONTS_DIR / filename
        if path.exists():
            faces.append(
                f"@font-face{{font-family:'{family}';src:url({data_uri(path, 'font/ttf')}) "
                f"format('{fmt}');font-weight:{weight};font-style:normal;}}"
            )
    inter = FONTS_DIR / "Inter-Variable.ttf"
    if inter.exists():
        faces.append(
            f"@font-face{{font-family:'Inter';src:url({data_uri(inter, 'font/ttf')}) "
            "format('truetype-variations');font-weight:100 900;font-style:normal;}"
        )
    return "\n".join(faces)


def icon_svg(name: str, size: int, color: str, stroke_width: float = 2.0) -> str:
    body = ICON_PATHS.get(name, ICON_PATHS["target"])
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


def pick_chip_icon(text: str) -> str:
    low = text.lower()
    for keywords, icon in CHIP_ICON_KEYWORDS:
        if any(k in low for k in keywords):
            return icon
    return "target"


def measure_headline_px(text: str, size: int) -> float:
    """Largura estimada da linha em Poppins Bold. Usa PIL quando disponível."""
    try:
        from PIL import ImageFont

        font_path = FONTS_DIR / "Poppins-Bold.ttf"
        if font_path.exists():
            fnt = ImageFont.truetype(str(font_path), size=size)
            return fnt.getbbox(text)[2]
    except Exception:
        pass
    return len(text) * size * 0.60


def fit_headline_size(lines: list[str], max_width: int, base: int, minimum: int = 50) -> int:
    size = base
    longest = max(lines, key=lambda t: measure_headline_px(t, base)) if lines else ""
    while size > minimum and measure_headline_px(longest, size) > max_width:
        size -= 2
    return size


# ---------------------------------------------------------------------------
# Normalização do config (portada do motor anterior, com extensões)
# ---------------------------------------------------------------------------

def infer_visual_type(text_blob: str) -> str:
    t = (text_blob or "").lower()
    if any(k in t for k in ("setor", "setores", "setorial")):
        return "sectors"
    if any(k in t for k in ("drawdown", "queda", "máxima", "maxima", "p75", "p90", "p95")):
        return "drawdown"
    # Séries temporais reais continuam como gráfico de linha.
    if any(k in t for k in ("ciclo", "ciclos", "ocorrência", "ocorrencias", "comportamento",
                            "recuperação", "recuperacao", "evolução", "evolucao",
                            "ao longo do tempo", "série histórica", "serie historica")):
        return "cycles"
    # KPIs/indicadores explícitos -> tiles de estatística.
    if any(k in t for k in ("kpi", "indicador", "indicadores", "métrica", "metrica",
                            "métricas", "metricas", "estatística", "estatistica", "percentil")):
        return "stats"
    # Default conceitual: cards numerados (não mais gráfico de linha).
    return "steps"


def normalize_spec(spec: dict[str, Any]) -> dict[str, Any]:
    spec = dict(spec)
    spec.setdefault("format", "feed_4x5")

    visual = dict(spec.get("visual") or {})
    if not visual.get("type"):
        blob = " ".join(
            [
                str(spec.get("headline", "")),
                " ".join(str(i.get("text", "")) for i in spec.get("headline_lines", []) or []),
                str(spec.get("subtitle", "")),
                " ".join(str(x) for x in spec.get("features", []) or []),
            ]
        )
        visual["type"] = infer_visual_type(blob)
    spec["visual"] = visual

    spec.setdefault("cta", "Conheça o Asset Lens")
    spec.setdefault("disclaimer", DEFAULT_DISCLAIMER)

    if not spec.get("headline_lines") and spec.get("headline"):
        spec["headline_lines"] = [{"text": spec["headline"], "color": "white"}]

    # `features` legado vira `chips` com ícone automático.
    if not spec.get("chips") and spec.get("features"):
        spec["chips"] = [{"text": str(f)} for f in spec["features"]]
    chips = []
    for chip in spec.get("chips") or []:
        if isinstance(chip, str):
            chip = {"text": chip}
        chip = dict(chip)
        chip.setdefault("icon", pick_chip_icon(chip.get("text", "")))
        chips.append(chip)
    spec["chips"] = chips[:4]

    if not spec.get("eyebrow"):
        spec["eyebrow"] = {
            "cycles": "COMPORTAMENTO HISTÓRICO",
            "drawdown": "DRAWDOWN POR ATIVO",
            "sectors": "LEITURA POR SETORES",
            "screenshot": "PAINEL INFORMACIONAL",
            "steps": "COMO FUNCIONA",
            "stats": "NÚMEROS EM CONTEXTO",
        }.get(visual.get("type", ""), "PAINEL INFORMACIONAL")
    spec.setdefault("eyebrow_icon", "grid")

    # Compat: background_monogram_mode -> watermark.
    spec.setdefault("watermark", spec.get("background_monogram_mode", "auto"))
    return spec


def watermark_enabled(spec: dict[str, Any]) -> bool:
    mode = str(spec.get("watermark", "auto")).lower().strip()
    if mode in {"off", "false", "0", "never"}:
        return False
    if mode in {"on", "true", "1", "always"}:
        return True
    if spec.get("format") == "story_9x16":
        return False
    if (spec.get("visual") or {}).get("type") == "screenshot":
        return False
    return True


# ---------------------------------------------------------------------------
# Curvas SVG
# ---------------------------------------------------------------------------

def catmull_rom_path(points: list[tuple[float, float]]) -> str:
    """Converte pontos em um caminho cúbico suave (Catmull-Rom -> Bézier)."""
    if len(points) < 2:
        return ""
    d = [f"M{points[0][0]:.1f},{points[0][1]:.1f}"]
    pts = [points[0]] + points + [points[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(
            f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        )
    return " ".join(d)


def values_to_points(values: list[float], w: float, h: float, pad_x: float, pad_top: float, pad_bottom: float) -> list[tuple[float, float]]:
    n = max(2, len(values))
    span_x = w - 2 * pad_x
    span_y = h - pad_top - pad_bottom
    pts = []
    for i, v in enumerate(values):
        x = pad_x + span_x * i / (n - 1)
        y = pad_top + max(0.0, min(1.0, float(v))) * span_y
        pts.append((x, y))
    return pts


def chart_grid(w: float, h: float, rows: int = 4, cols: int = 7) -> str:
    lines = []
    for i in range(rows + 1):
        y = h * i / rows
        lines.append(
            f'<line x1="0" y1="{y:.1f}" x2="{w}" y2="{y:.1f}" stroke="rgba(63,116,150,0.16)" stroke-width="1"/>'
        )
    for i in range(cols + 1):
        x = w * i / cols
        lines.append(
            f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{h}" stroke="rgba(63,116,150,0.12)" stroke-width="1"/>'
        )
    return "".join(lines)


def glow_filters(colors: list[str]) -> str:
    filters = []
    for i, _c in enumerate(colors):
        filters.append(
            f'<filter id="glow{i}" x="-40%" y="-40%" width="180%" height="180%">'
            '<feGaussianBlur stdDeviation="7" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
            "</filter>"
        )
    return "".join(filters)


# ---------------------------------------------------------------------------
# Visuais
# ---------------------------------------------------------------------------

# Acentos rotativos para cards de features (só cores frias; vermelho/amarelo
# ficam reservados a indicadores, conforme QUALITY_STANDARD.md).
STEP_ACCENTS = ["cyan", "teal", "blue", "green"]


def visual_cycles(visual: dict[str, Any]) -> str:
    w, h = 920.0, 470.0
    series = visual.get("series") or [
        {"label": "Recuperação forte", "color": "cyan",
         "values": [0.30, 0.31, 0.44, 0.36, 0.24, 0.15, 0.10, 0.07]},
        {"label": "Recuperação lenta", "color": "teal",
         "values": [0.30, 0.33, 0.48, 0.55, 0.48, 0.40, 0.34, 0.29]},
        {"label": "Queda profunda", "color": "blue",
         "values": [0.30, 0.36, 0.62, 0.84, 0.72, 0.62, 0.55, 0.50]},
    ]
    baseline_frac = float(visual.get("baseline_frac", 0.30))
    baseline_label = visual.get("baseline_label", "topo do ciclo")

    colors = [color_value(s.get("color"), "cyan") for s in series]
    chart_h = h - 66
    baseline_y = 14 + baseline_frac * (chart_h - 34)

    parts = [
        f'<svg class="chart" viewBox="0 0 {w:.0f} {h:.0f}">',
        f"<defs>{glow_filters(colors)}</defs>",
        f'<g transform="translate(0,6)">{chart_grid(w, chart_h, rows=4, cols=8)}</g>',
        f'<line x1="0" y1="{baseline_y:.1f}" x2="{w}" y2="{baseline_y:.1f}" '
        'stroke="rgba(244,247,251,0.55)" stroke-width="2" stroke-dasharray="7 9"/>',
        f'<text x="6" y="{baseline_y - 12:.1f}" class="svg-label">{esc(baseline_label)}</text>',
    ]
    for i, s in enumerate(series):
        pts = values_to_points([float(v) for v in s.get("values", [])], w, chart_h, 8, 14, 20)
        if len(pts) < 2:
            continue
        path = catmull_rom_path(pts)
        c = colors[i]
        parts.append(
            f'<path d="{path}" fill="none" stroke="{c}" stroke-width="4.5" '
            f'stroke-linecap="round" filter="url(#glow{i})"/>'
        )
        ex, ey = pts[-1]
        parts.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="10" fill="{c}" opacity="0.28"/>')
        parts.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="6" fill="{c}"/>')
    parts.append("</svg>")

    legend = "".join(
        f'<span class="legend-item"><i style="background:{colors[i]}"></i>{esc(s.get("label", ""))}</span>'
        for i, s in enumerate(series)
    )
    parts.append(f'<div class="legend">{legend}</div>')
    return "".join(parts)


def visual_drawdown(visual: dict[str, Any]) -> str:
    w, h = 920.0, 470.0
    values = [float(v) for v in (visual.get("values") or
              [0.06, 0.14, 0.24, 0.16, 0.50, 0.74, 0.56, 0.40, 0.63, 0.44, 0.30, 0.20])]
    levels = visual.get("levels") or [
        {"label": "P75", "frac": 0.36, "color": "blue"},
        {"label": "P90", "frac": 0.52, "color": "yellow"},
        {"label": "P95", "frac": 0.66, "color": "red"},
    ]
    x_labels = visual.get("x_labels") or []

    chart_h = h - 60
    top_y = 44
    pts = values_to_points(values, w, chart_h, 8, top_y, 26)
    line = catmull_rom_path(pts)
    area = line + f" L{pts[-1][0]:.1f},{top_y} L{pts[0][0]:.1f},{top_y} Z"
    red = PALETTE["red"]

    parts = [
        f'<svg class="chart" viewBox="0 0 {w:.0f} {h:.0f}">',
        f'<defs>{glow_filters([red])}'
        f'<linearGradient id="ddfill" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{red}" stop-opacity="0.15"/>'
        f'<stop offset="100%" stop-color="{red}" stop-opacity="0.03"/>'
        "</linearGradient></defs>",
        f'<g transform="translate(0,6)">{chart_grid(w, chart_h, rows=4, cols=8)}</g>',
        f'<line x1="0" y1="{top_y}" x2="{w}" y2="{top_y}" stroke="rgba(244,247,251,0.45)" stroke-width="2"/>',
        f'<text x="6" y="{top_y - 14}" class="svg-label">máxima histórica</text>',
        f'<path d="{area}" fill="url(#ddfill)" stroke="none"/>',
        f'<path d="{line}" fill="none" stroke="{red}" stroke-width="4.5" stroke-linecap="round" filter="url(#glow0)"/>',
    ]
    for lv in levels:
        y = top_y + float(lv.get("frac", 0.5)) * (chart_h - top_y - 26)
        c = color_value(lv.get("color"), "yellow")
        label = esc(lv.get("label", ""))
        parts.append(
            f'<line x1="0" y1="{y:.1f}" x2="{w - 84}" y2="{y:.1f}" stroke="{c}" '
            'stroke-width="2" stroke-dasharray="8 8" opacity="0.85"/>'
        )
        parts.append(f'<text x="{w - 74:.1f}" y="{y + 6:.1f}" class="svg-level" fill="{c}">{label}</text>')
    if x_labels:
        n = len(x_labels)
        for i, lb in enumerate(x_labels):
            x = 8 + (w - 16) * i / max(1, n - 1)
            anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
            parts.append(
                f'<text x="{x:.1f}" y="{h - 12:.1f}" class="svg-axis" text-anchor="{anchor}">{esc(lb)}</text>'
            )
    parts.append("</svg>")

    legend_items = visual.get("legend") or ["Distância da máxima", "Faixas quantitativas históricas"]
    legend_colors = [red, PALETTE["yellow"]]
    legend = "".join(
        f'<span class="legend-item"><i style="background:{legend_colors[min(i, 1)]}"></i>{esc(t)}</span>'
        for i, t in enumerate(legend_items[:2])
    )
    parts.append(f'<div class="legend">{legend}</div>')
    return "".join(parts)


def visual_sectors(visual: dict[str, Any]) -> str:
    items = visual.get("items") or [
        {"name": "Financeiro", "value": 62, "color": "green"},
        {"name": "Utilidades", "value": 57, "color": "yellow"},
        {"name": "Energia", "value": 53, "color": "cyan"},
        {"name": "Materiais", "value": 49, "color": "blue"},
        {"name": "Indústria", "value": 46, "color": "teal"},
        {"name": "Tecnologia", "value": 41, "color": "blue"},
    ]
    value_suffix = visual.get("value_suffix", "")
    value_label = visual.get("value_label", "média do grupo")
    cards = []
    for item in items[:6]:
        c = color_value(item.get("color"), "cyan")
        value = item.get("value", 0)
        try:
            pct = max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            pct = 0.0
        sub = str(item.get("sub", "")).strip()
        sub_html = f'<div class="sector-desc">{esc(sub)}</div>' if sub else ""
        cards.append(
            '<div class="sector-card" style="border-color:' + c + '55">'
            f'<div class="sector-name">{esc(item.get("name", ""))}</div>'
            f'<div class="sector-value" style="color:{c}">{esc(value)}{esc(value_suffix)}'
            f'<span class="sector-sub">{esc(value_label)}</span></div>'
            f"{sub_html}"
            '<div class="sector-bar"><i style="width:' + f"{pct:.0f}%" + ";background:" + c + '"></i></div>'
            "</div>"
        )
    cols = 2 if len(items) <= 4 else 3
    return (
        f'<div class="sector-grid" style="grid-template-columns:repeat({cols},1fr)">'
        + "".join(cards)
        + "</div>"
    )


def visual_steps(visual: dict[str, Any]) -> str:
    """Grade de cards numerados (1..N) com ícone, título e descrição.

    Padrão dos carrosséis aprovados (features / como funciona). Não inventa
    números: usa apenas títulos e descrições conceituais.
    """
    items = visual.get("items") or [
        {"icon": "trend-down", "title": "Queda desde a máxima",
         "desc": "Acompanhe a distância até o pico mais recente."},
        {"icon": "target", "title": "Faixas de referência",
         "desc": "Compare com P75, P90 e P95 do próprio ativo."},
        {"icon": "clock", "title": "Contexto histórico",
         "desc": "Veja em que períodos ocorreram as maiores quedas."},
    ]
    items = items[:4]
    n = len(items)
    cols = 3 if n == 3 else (1 if n <= 1 else 2)
    cards = []
    for i, item in enumerate(items):
        accent = color_value(item.get("color"), STEP_ACCENTS[i % len(STEP_ACCENTS)])
        icon = item.get("icon", "target")
        desc = str(item.get("desc", "")).strip()
        desc_html = f'<div class="step-desc">{esc(desc)}</div>' if desc else ""
        cards.append(
            '<div class="step-card" style="border-color:' + accent + '44">'
            '<div class="step-top">'
            f'<span class="step-badge" style="color:{accent};border-color:{accent}66">{i + 1}</span>'
            f'<span class="step-icon" style="border-color:{accent}55">{icon_svg(icon, 30, accent, 2.1)}</span>'
            "</div>"
            f'<div class="step-title">{esc(item.get("title", ""))}</div>'
            f"{desc_html}"
            "</div>"
        )
    return (
        f'<div class="step-grid" style="grid-template-columns:repeat({cols},1fr)">'
        + "".join(cards)
        + "</div>"
    )


def visual_stats(visual: dict[str, Any]) -> str:
    """Tiles de KPI: rótulo + valor grande (colorido) + sublinha opcional.

    `value` é uma string já formatada (ex.: "-56,6%", "+207,7%", "42").
    Vermelho/amarelo são permitidos aqui por serem indicadores.
    """
    items = visual.get("items") or [
        {"value": "-56,6%", "label": "Pior drawdown", "sub": "out/2008", "color": "red"},
        {"value": "-33,7%", "label": "P95 histórico", "color": "yellow"},
        {"value": "-19,0%", "label": "P75 histórico", "color": "blue"},
    ]
    items = items[:6]
    n = len(items)
    cols = n if n <= 3 else (2 if n == 4 else 3)
    tiles = []
    for item in items:
        accent = color_value(item.get("color"), "cyan")
        sub = str(item.get("sub", "")).strip()
        sub_html = f'<div class="stat-sub">{esc(sub)}</div>' if sub else ""
        tiles.append(
            '<div class="stat-tile" style="border-color:' + accent + '3a">'
            f'<div class="stat-label">{esc(item.get("label", ""))}</div>'
            f'<div class="stat-value" style="color:{accent}">{esc(item.get("value", ""))}</div>'
            f"{sub_html}"
            "</div>"
        )
    return (
        f'<div class="stat-grid" style="grid-template-columns:repeat({cols},1fr)">'
        + "".join(tiles)
        + "</div>"
    )


def visual_screenshot(visual: dict[str, Any], panel_inner_w: int, panel_inner_h: int) -> str:
    path = Path(str(visual.get("screenshot_path", "")))
    if not path.exists():
        raise FileNotFoundError(f"Screenshot não encontrado: {path}")

    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    uri = data_uri(path, mime)

    # Dimensão real para calcular o encaixe do cartão principal.
    iw, ih = 1600, 900
    try:
        from PIL import Image

        with Image.open(path) as img:
            iw, ih = img.size
    except Exception:
        pass

    aspect = iw / max(1, ih)

    # O hero preenche o painel via CSS (object-fit: contain). O inset de detalhe
    # vem DESLIGADO por padrão; `detail` explícito liga, `detail: false` desliga.
    raw_detail = visual.get("detail")
    show_detail = bool(raw_detail) if raw_detail is not None else False
    detail = raw_detail if isinstance(raw_detail, dict) else {}
    caption = str(visual.get("caption", "")).strip()

    inset_html = ""
    if show_detail:
        # x/y = centro do ponto de interesse, em % da imagem original.
        zoom = max(1.2, float(detail.get("zoom", 2.2)))
        fx = float(detail.get("x", 50)) / 100.0
        fy = float(detail.get("y", 30)) / 100.0
        detail_label = detail.get("label", "Destaque do painel")
        inset_w = int(panel_inner_w * 0.30)
        inset_h = int(inset_w * 0.66)

        # background-size: zoom relativo à largura do box.
        scaled_w = zoom
        scaled_h = zoom * (inset_w / aspect) / inset_h  # altura escalada / altura do box
        def bg_pos(center: float, scale: float) -> float:
            if scale <= 1.0:
                return 50.0
            return max(0.0, min(100.0, 100.0 * (0.5 - center * scale) / (1.0 - scale)))

        pos_x = bg_pos(fx, scaled_w)
        pos_y = bg_pos(fy, scaled_h)
        inset_html = (
            f'<div class="shot-inset" style="width:{inset_w}px;height:{inset_h}px;'
            f"background-image:url({uri});background-size:{zoom * 100:.0f}% auto;"
            f'background-position:{pos_x:.1f}% {pos_y:.1f}%">'
            f'<span class="shot-chip">{icon_svg("zoom", 15, PALETTE["cyan"], 2.2)}{esc(detail_label)}</span>'
            "</div>"
        )

    return f"""
      <div class="shot-ambient" style="background-image:url({uri})"></div>
      <div class="shot-ambient-overlay"></div>
      <div class="shot-stage">
        <img class="shot-hero" src="{uri}" alt="">
      </div>
      {inset_html}
      {f'<div class="shot-caption">{esc(caption)}</div>' if caption else ''}
    """


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------

def build_slide_html(spec: dict[str, Any]) -> str:
    spec = normalize_spec(spec)
    fmt = spec.get("format", "feed_4x5")
    page_w, page_h = DIMENSIONS.get(fmt, DIMENSIONS["feed_4x5"])
    story = fmt == "story_9x16"

    pad_x = 60 if not story else 66
    visual = spec.get("visual") or {}
    vtype = visual.get("type", "cycles")

    # Screenshots (e o flag `layout: "hero"`) compactam as margens verticais para
    # o painel/imagem real crescer e ficar legível.
    page_class = "page"
    if vtype == "screenshot" or str(spec.get("layout", "")).lower() == "hero":
        page_class = "page shot-mode"

    logo_path = Path(str(spec.get("brand_logo_path") or DEFAULT_LOGO))
    logo_uri = data_uri(logo_path, "image/png") if logo_path.exists() else ""

    # Headline com ajuste de corpo pela linha mais longa.
    headline_lines = spec.get("headline_lines") or []
    texts = [str(i.get("text", "")).strip() for i in headline_lines if str(i.get("text", "")).strip()]
    base_size = int(spec.get("headline_size", 0)) or (86 if not story else 92)
    hsize = fit_headline_size(texts, page_w - 2 * pad_x, base_size)
    headline_html = "".join(
        f'<span style="color:{color_value(item.get("color"), "white")}">{esc(str(item.get("text", "")).strip())}</span>'
        for item in headline_lines[:3]
        if str(item.get("text", "")).strip()
    )

    subtitle = str(spec.get("subtitle", "")).strip()
    chips = spec.get("chips") or []
    chips_html = "".join(
        f'<span class="chip">{icon_svg(chip.get("icon", "target"), 21, PALETTE["cyan"], 2.1)}<b>{esc(chip.get("text", ""))}</b></span>'
        for chip in chips
    )

    panel_title = visual.get("panel_title", "")
    panel_title_right = visual.get("panel_title_right", "")
    panel_head = ""
    if panel_title or panel_title_right:
        panel_head = (
            '<div class="panel-head">'
            f'<span>{esc(panel_title)}</span><em>{esc(panel_title_right)}</em>'
            "</div>"
        )

    panel_inner_w = page_w - 2 * pad_x - 2 * 34
    panel_inner_h = (520 if not story else 760) - 2 * 30
    if vtype == "screenshot":
        visual_html = visual_screenshot(visual, panel_inner_w, panel_inner_h)
        panel_class = "panel panel-shot"
    elif vtype == "drawdown":
        visual_html = visual_drawdown(visual)
        panel_class = "panel"
    elif vtype == "sectors":
        visual_html = visual_sectors(visual)
        panel_class = "panel"
    elif vtype == "steps":
        visual_html = visual_steps(visual)
        panel_class = "panel"
    elif vtype == "stats":
        visual_html = visual_stats(visual)
        panel_class = "panel"
    elif vtype == "none":
        visual_html = ""
        panel_class = "panel panel-empty"
    else:
        visual_html = visual_cycles(visual)
        panel_class = "panel"

    cta = str(spec.get("cta", "")).strip()
    cta_secondary = str(spec.get("cta_secondary", "")).strip()
    disclaimer = str(spec.get("disclaimer", "")).strip()
    slide_number = str(spec.get("slide_number", "")).strip()
    eyebrow = str(spec.get("eyebrow", "")).strip()

    watermark_html = ""
    if watermark_enabled(spec):
        letter = esc(str(spec.get("watermark_letter", "A"))[:2])
        watermark_html = f'<div class="watermark">{letter}</div>'

    frame_html = '<div class="outer-frame"></div>' if spec.get("outer_frame") else ""

    slide_pill = f'<span class="slide-pill">{esc(slide_number)}</span>' if slide_number else ""

    css = f"""
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    {font_face_css()}
    :root {{
      --cyan: {PALETTE['cyan']}; --teal: {PALETTE['teal']}; --blue: {PALETTE['blue']};
      --white: {PALETTE['white']}; --text2: {PALETTE['text_2']}; --text3: {PALETTE['text_3']};
      --surface: {PALETTE['surface']}; --surface2: {PALETTE['surface_2']};
    }}
    html, body {{ width: {page_w}px; height: {page_h}px; overflow: hidden; }}
    body {{
      font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
      background:
        radial-gradient(58% 34% at 86% 12%, rgba(34,216,244,0.10), transparent 70%),
        radial-gradient(44% 30% at 8% 58%, rgba(21,232,209,0.05), transparent 70%),
        radial-gradient(50% 32% at 84% 86%, rgba(65,180,255,0.07), transparent 70%),
        linear-gradient(180deg, {PALETTE['bg_top']} 0%, {PALETTE['bg_bottom']} 100%);
      position: relative; color: var(--white);
    }}
    .dots {{
      position: absolute; inset: 0;
      background-image: radial-gradient(rgba(143,176,205,0.13) 1.1px, transparent 1.3px);
      background-size: 27px 27px;
      -webkit-mask-image: radial-gradient(70% 55% at 78% 30%, rgba(0,0,0,0.9), transparent 75%);
              mask-image: radial-gradient(70% 55% at 78% 30%, rgba(0,0,0,0.9), transparent 75%);
    }}
    .vignette {{
      position: absolute; inset: 0;
      background: radial-gradient(125% 92% at 50% 40%, transparent 58%, rgba(0,0,0,0.46) 100%);
    }}
    .watermark {{
      position: absolute; right: -14px; top: 10%;
      font-family: 'Poppins', 'Segoe UI', sans-serif; font-weight: 700;
      font-size: {int(page_h * 0.34)}px; line-height: 1;
      color: transparent; -webkit-text-stroke: 2.5px rgba(34,216,244,0.085);
      text-shadow: 0 0 60px rgba(34,216,244,0.05);
    }}
    .outer-frame {{
      position: absolute; inset: 22px; border-radius: 32px;
      border: 1.5px solid rgba(34,216,244,0.34);
      box-shadow: 0 0 34px rgba(34,216,244,0.10), inset 0 0 26px rgba(34,216,244,0.05);
      pointer-events: none;
    }}
    .page {{
      position: relative; width: 100%; height: 100%;
      padding: {52 if not story else 76}px {pad_x}px {40 if not story else 62}px;
      display: flex; flex-direction: column;
    }}
    header {{ display: flex; align-items: center; gap: 18px; }}
    header img.logo {{ width: {62 if not story else 68}px; height: {62 if not story else 68}px; filter: drop-shadow(0 0 14px rgba(34,216,244,0.35)); }}
    .wordmark {{ font-family: 'Poppins', 'Segoe UI', sans-serif; font-weight: 600; font-size: {34 if not story else 38}px; letter-spacing: 0.2px; }}
    .wordmark b {{ color: var(--cyan); font-weight: 600; }}
    .slide-pill {{
      margin-left: auto; font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 22px;
      color: var(--cyan); border: 1.5px solid rgba(34,216,244,0.55); border-radius: 999px;
      padding: 8px 20px; background: rgba(10,24,40,0.55);
    }}
    .eyebrow {{
      margin-top: {34 if not story else 52}px; display: inline-flex; align-items: center; gap: 12px;
      width: fit-content; padding: 12px 24px 12px 18px; border-radius: 14px;
      border: 1.5px solid rgba(21,232,209,0.50); background: rgba(10,24,40,0.55);
      color: var(--teal); font-weight: 650; font-size: 20px; letter-spacing: 3.2px;
      box-shadow: 0 0 26px rgba(21,232,209,0.10);
    }}
    h1 {{
      margin-top: {30 if not story else 44}px;
      font-family: 'Poppins', 'Segoe UI', sans-serif; font-weight: 700;
      font-size: {hsize}px; line-height: 1.08; letter-spacing: -0.5px;
    }}
    h1 span {{ display: block; }}
    .subtitle {{
      margin-top: {22 if not story else 30}px; max-width: {page_w - 2 * pad_x - 40}px;
      color: var(--text2); font-size: {30 if not story else 33}px; line-height: 1.42; font-weight: 420;
    }}
    .chips {{ margin-top: {26 if not story else 34}px; display: flex; gap: 14px; flex-wrap: wrap; }}
    .chip {{
      display: inline-flex; align-items: center; gap: 11px;
      border: 1.5px solid rgba(34,216,244,0.36); background: rgba(10,24,40,0.62);
      border-radius: 999px; padding: 12px 22px 12px 16px;
      box-shadow: 0 0 18px rgba(34,216,244,0.08);
    }}
    .chip b {{ font-weight: 560; font-size: 22px; color: var(--white); }}
    .visual-wrap {{ flex: 1; min-height: 0; display: flex; margin-top: {30 if not story else 38}px; }}
    .panel {{
      flex: 1; position: relative; border-radius: 30px; overflow: hidden;
      background: linear-gradient(165deg, rgba(16,38,60,0.62) 0%, rgba(7,17,29,0.78) 100%);
      border: 1.5px solid rgba(34,216,244,0.30);
      box-shadow: 0 30px 70px rgba(0,0,0,0.55), 0 0 46px rgba(34,216,244,0.10),
                  inset 0 1px 0 rgba(255,255,255,0.07);
      padding: 30px 34px 24px; display: flex; flex-direction: column;
    }}
    .panel-head {{
      display: flex; justify-content: space-between; align-items: center;
      font-weight: 640; font-size: 19px; letter-spacing: 2.4px; margin-bottom: 12px;
    }}
    .panel-head span {{ color: var(--text2); }}
    .panel-head em {{ color: var(--cyan); font-style: normal; }}
    .chart {{ flex: 1; width: 100%; min-height: 0; }}
    .svg-label {{ font-family: 'Inter', sans-serif; font-size: 20px; fill: var(--text3); }}
    .svg-level {{ font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 640; }}
    .svg-axis {{ font-family: 'Inter', sans-serif; font-size: 16px; fill: var(--text3); }}
    .legend {{ display: flex; gap: 34px; padding: 14px 6px 2px; }}
    .legend-item {{ display: inline-flex; align-items: center; gap: 10px; color: var(--text2); font-size: 21px; font-weight: 520; }}
    .legend-item i {{ width: 14px; height: 14px; border-radius: 50%; display: inline-block; }}
    .sector-grid {{ flex: 1; display: grid; grid-template-columns: 1fr 1fr 1fr; grid-auto-rows: 1fr; gap: 16px; }}
    .sector-card {{
      border: 1.5px solid; border-radius: 20px; background: rgba(10,24,40,0.66);
      padding: 20px 22px; display: flex; flex-direction: column;
      justify-content: center; gap: 20px;
    }}
    .sector-name {{ font-weight: 600; font-size: 22px; }}
    .sector-value {{ font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 40px; line-height: 1; display: flex; align-items: baseline; gap: 10px; }}
    .sector-sub {{ font-family: 'Inter', sans-serif; font-weight: 460; font-size: 16px; color: var(--text3); }}
    .sector-desc {{ color: var(--text3); font-size: 19px; line-height: 1.45; font-weight: 440; }}
    .sector-bar {{ height: 9px; border-radius: 6px; background: rgba(3,10,18,0.9); overflow: hidden; }}
    .sector-bar i {{ display: block; height: 100%; border-radius: 6px; }}
    .step-grid {{ flex: 1; display: grid; grid-auto-rows: 1fr; gap: 18px; }}
    .step-card {{
      border: 1.5px solid; border-radius: 20px; background: rgba(10,24,40,0.66);
      padding: 24px; display: flex; flex-direction: column; gap: 14px;
    }}
    .step-top {{ display: flex; align-items: center; gap: 14px; }}
    .step-badge {{
      font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 30px; line-height: 1;
      width: 46px; height: 46px; border-radius: 12px; border: 1.5px solid;
      display: inline-flex; align-items: center; justify-content: center; background: rgba(3,10,18,0.55);
    }}
    .step-icon {{
      width: 46px; height: 46px; border-radius: 12px; border: 1.5px solid; margin-left: auto;
      display: inline-flex; align-items: center; justify-content: center; background: rgba(3,10,18,0.35);
    }}
    .step-title {{ font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 26px; line-height: 1.15; }}
    .step-desc {{ color: var(--text3); font-size: 20px; line-height: 1.45; font-weight: 440; }}
    .stat-grid {{ flex: 1; display: grid; grid-auto-rows: 1fr; gap: 16px; }}
    .stat-tile {{
      border: 1.5px solid; border-radius: 18px; background: rgba(10,24,40,0.66);
      padding: 22px 24px; display: flex; flex-direction: column; justify-content: center; gap: 8px;
    }}
    .stat-label {{ color: var(--text3); font-size: 18px; font-weight: 560; letter-spacing: 1.6px; text-transform: uppercase; }}
    .stat-value {{ font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 46px; line-height: 1; }}
    .stat-sub {{ color: var(--text3); font-size: 18px; font-weight: 460; }}
    .panel-shot {{ padding: 0; }}
    .shot-ambient {{ position: absolute; inset: 0; background-size: cover; background-position: center; filter: blur(30px) brightness(0.52) saturate(0.9); transform: scale(1.12); }}
    .shot-ambient-overlay {{ position: absolute; inset: 0; background: linear-gradient(170deg, rgba(3,12,20,0.50), rgba(2,8,14,0.72)); }}
    .shot-stage {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; padding: 26px; }}
    .shot-hero {{
      max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain; display: block;
      border-radius: 18px; border: 2px solid rgba(34,216,244,0.55);
      box-shadow: 0 26px 60px rgba(0,0,0,0.6), 0 0 40px rgba(34,216,244,0.16);
    }}
    .shot-inset {{
      position: absolute; right: 26px; bottom: 26px; border-radius: 16px;
      border: 1.5px solid rgba(244,247,251,0.35); background-repeat: no-repeat;
      box-shadow: 0 18px 44px rgba(0,0,0,0.65), 0 0 30px rgba(34,216,244,0.12);
      outline: 8px solid rgba(8,22,36,0.85);
    }}
    .shot-chip {{
      position: absolute; top: -18px; left: 12px; display: inline-flex; align-items: center; gap: 7px;
      background: {PALETTE['surface_2']}; border: 1.5px solid rgba(34,216,244,0.6);
      color: var(--cyan); font-size: 16px; font-weight: 600; border-radius: 999px; padding: 6px 14px;
    }}
    .shot-caption {{ position: absolute; left: 26px; bottom: 22px; color: var(--text3); font-size: 17px; font-weight: 520; }}
    .page.shot-mode .eyebrow {{ margin-top: {22 if not story else 34}px; }}
    .page.shot-mode h1 {{ margin-top: {20 if not story else 30}px; }}
    .page.shot-mode .subtitle {{ margin-top: {14 if not story else 20}px; }}
    .page.shot-mode .chips {{ margin-top: {16 if not story else 22}px; }}
    .page.shot-mode .visual-wrap {{ margin-top: {20 if not story else 26}px; }}
    .cta-row {{ margin-top: {30 if not story else 40}px; display: flex; flex-direction: column; align-items: center; gap: 12px; }}
    .cta {{
      display: inline-flex; align-items: center; gap: 18px;
      min-width: 62%; justify-content: center;
      padding: {20 if not story else 24}px 38px; border-radius: 999px;
      background: linear-gradient(180deg, rgba(16,38,58,0.92), rgba(8,20,34,0.92));
      border: 1.5px solid rgba(34,216,244,0.55);
      box-shadow: 0 0 38px rgba(34,216,244,0.20), inset 0 1px 0 rgba(255,255,255,0.08);
      font-family: 'Poppins', 'Segoe UI', sans-serif; font-weight: 600; font-size: {30 if not story else 33}px;
    }}
    .cta .chev {{ margin-left: 6px; display: inline-flex; }}
    .cta-secondary {{ color: var(--cyan); font-size: 21px; font-weight: 520; letter-spacing: 0.3px; }}
    .disclaimer {{
      margin-top: {22 if not story else 30}px; display: flex; align-items: center; justify-content: center;
      gap: 10px; color: var(--text3); font-size: {19 if not story else 21}px; font-weight: 460;
    }}
    """

    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
  <div class="dots"></div>
  {watermark_html}
  <div class="vignette"></div>
  {frame_html}
  <div class="{page_class}">
    <header>
      {f'<img class="logo" src="{logo_uri}" alt="">' if logo_uri else ''}
      <span class="wordmark">Asset <b>Lens</b></span>
      {slide_pill}
    </header>
    {f'<span class="eyebrow">{icon_svg(spec.get("eyebrow_icon", "grid"), 21, PALETTE["teal"], 2.1)}{esc(eyebrow)}</span>' if eyebrow else ''}
    <h1>{headline_html}</h1>
    {f'<p class="subtitle">{esc(subtitle)}</p>' if subtitle else ''}
    {f'<div class="chips">{chips_html}</div>' if chips_html else ''}
    <div class="visual-wrap">
      <div class="{panel_class}">
        {panel_head}
        {visual_html}
      </div>
    </div>
    {f'''<div class="cta-row">
      <span class="cta">{icon_svg("search", 30, PALETTE["cyan"], 2.4)}{esc(cta)}<span class="chev">{icon_svg("chevron", 28, PALETTE["cyan"], 2.6)}</span></span>
      {f'<span class="cta-secondary">{esc(cta_secondary)}</span>' if cta_secondary else ''}
    </div>''' if cta else ''}
    {f'<div class="disclaimer">{icon_svg("shield", 21, PALETTE["text_3"], 2.0)}{esc(disclaimer)}</div>' if disclaimer else ''}
  </div>
</body>
</html>"""
    return doc


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Gera o HTML de um slide para depuração.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    spec = json.loads(Path(args.config).read_text(encoding="utf-8"))
    Path(args.out).write_text(build_slide_html(spec), encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()

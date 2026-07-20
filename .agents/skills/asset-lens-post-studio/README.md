# Asset Lens Post Studio

Skill que transforma um tema ou um screenshot do Asset Lens em um post de
Instagram finalizado: imagem premium + copy, salvos em
`instagram/AAAA-MM-DD-<slug>/` na raiz do projeto.

A implementação canônica fica em `.agents/skills/asset-lens-post-studio/` e é
usada por Codex e GitHub Copilot. Claude Code usa um adaptador em
`.claude/skills/asset-lens-post-studio/` que aponta para esta mesma fonte.

## Como funciona

```text
render.json ──► scripts/build_html.py ──► render.html
                    (template premium: Poppins/Inter embutidas,
                     logo e screenshot como data URI, SVG charts)
render.html ──► Chrome/Edge headless (2x) ──► post.png (1080×1350)
copy.md     ──► escrita pelo agente (nunca por template)
tudo        ──► scripts/verify_output.py (proporção, disclaimer, lint)
```

Requisitos: Python 3.10+, Google Chrome ou Microsoft Edge instalados.
Pillow é instalado automaticamente num venv local da skill se faltar
(`ASSET_LENS_BROWSER` força um executável de navegador específico).

## Estrutura

```text
asset-lens-post-studio/
├── SKILL.md               # fluxo obrigatório do agente
├── QUALITY_STANDARD.md    # checklist + auto-revisão visual
├── brand_guide.md         # marca, paleta, tipografia
├── README.md
├── assets/
│   └── fonts/             # Poppins + Inter (OFL, embutidas no HTML)
├── references/
│   ├── approved_examples/ # autoridade visual do conjunto
│   ├── brand/             # logo_official.png (alpha)
│   ├── product-brief.md   # posicionamento e limites
│   ├── feature-catalog.md # recursos reais do produto
│   ├── compliance.md      # linguagem e blindagem editorial
│   └── messaging.md       # voz, pilares e CTAs
├── agents/
│   └── openai.yaml        # metadados opcionais do Codex
└── scripts/
    ├── build_html.py      # config JSON -> HTML autossuficiente
    ├── run.py             # HTML -> screenshot headless -> PNG final
    └── verify_output.py   # validação de entrega + lint de compliance
```

## Uso

```text
Claude/Copilot: /asset-lens-post-studio drawdown histórico
Codex:          $asset-lens-post-studio drawdown histórico
```

Execução manual (depuração):

```powershell
python .agents/skills/asset-lens-post-studio/scripts/run.py --config instagram/2026-07-19-tema/render.json
python .agents/skills/asset-lens-post-studio/scripts/verify_output.py instagram/2026-07-19-tema/post.png instagram/2026-07-19-tema/copy.md instagram/2026-07-19-tema/render.json
```

## Exemplos de visual customizado (dados conceituais)

```json
"visual": {
  "type": "cycles",
  "baseline_label": "topo do ciclo",
  "series": [
    {"label": "Recuperação forte", "color": "cyan",
     "values": [0.30, 0.31, 0.44, 0.36, 0.24, 0.15, 0.10, 0.07]}
  ]
}
```

```json
"visual": {
  "type": "drawdown",
  "panel_title": "DRAWDOWN — CONCEITO",
  "levels": [
    {"label": "P75", "frac": 0.36, "color": "blue"},
    {"label": "P90", "frac": 0.52, "color": "yellow"},
    {"label": "P95", "frac": 0.66, "color": "red"}
  ],
  "x_labels": ["início", "ciclo 1", "ciclo 2", "hoje"]
}
```

```json
"visual": {
  "type": "steps",
  "items": [
    {"icon": "trend-down", "title": "Queda desde a máxima",
     "desc": "Distância até o pico mais recente."},
    {"icon": "target", "title": "Faixas de referência",
     "desc": "P75, P90 e P95 do próprio ativo."},
    {"icon": "clock", "title": "Contexto histórico",
     "desc": "Em que períodos ocorreram as maiores quedas."}
  ]
}
```

```json
"visual": {
  "type": "stats",
  "items": [
    {"value": "-56,6%", "label": "Pior drawdown", "sub": "out/2008", "color": "red"},
    {"value": "-33,7%", "label": "P95 histórico", "color": "yellow"},
    {"value": "+15,4%", "label": "CAGR", "color": "green"}
  ]
}
```

```json
"visual": {
  "type": "screenshot",
  "screenshot_path": "C:/caminho/real.png",
  "detail": {"x": 82, "y": 14, "zoom": 2.4, "label": "Distribuição por zona"}
}
```

Os PNGs de `instagram/` não são versionados (ver `.gitignore` da raiz), mas a
entrega só termina quando eles existem e passam pelo verificador.

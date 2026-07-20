"""Valida os entregáveis de um post do Asset Lens.

Uso:
    python verify_output.py <post.png> [slide-02.png ...] <copy.md> [render.json]

Checa:
- existência de cada arquivo;
- PNG em proporção 4:5, 1:1 ou 9:16 com largura mínima de 1080;
- copy.md não vazia, com o disclaimer padrão e no máximo 4 hashtags;
- lint de compliance (termos proibidos) na copy e nos textos de configs JSON.

Sai com código 1 e mensagens claras em caso de falha.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

DISCLAIMER_MARKER = "não é recomendação de investimento"

# Padrões avaliados sobre texto normalizado (minúsculas, sem acentos).
FORBIDDEN_PATTERNS = [
    (r"\bganhe\b", "promessa de ganho ('ganhe')"),
    (r"\bganho[s]? garantido", "promessa de ganho garantido"),
    (r"\blucr\w*", "linguagem de lucro ('lucro', 'lucre', 'lucrar'...)"),
    (r"\brentabilidade garantida", "promessa de rentabilidade"),
    (r"\bretorno garantido", "promessa de retorno"),
    (r"\brenda garantida", "promessa de renda"),
    (r"\bgarantid[oa]s?\b", "linguagem de garantia de resultado"),
    (r"oportunidade (unica|imperdivel|garantida)", "apelo de oportunidade"),
    (r"\bsinal de compra\b", "sinal de compra"),
    (r"\bsinal de venda\b", "sinal de venda"),
    (r"\bcall de (compra|venda)\b", "call de compra/venda"),
    (r"\brecomendo\b", "tom de recomendação ('recomendo')"),
    (r"\brecomendamos\b", "tom de recomendação ('recomendamos')"),
    (r"\bnossa recomendacao\b", "tom de recomendação"),
    (r"\brecomendacao de (compra|venda)\b", "recomendação de compra/venda"),
    (r"\bpreco[- ]alvo\b", "preço-alvo"),
    (r"\bcompre\b", "imperativo de compra ('compre')"),
    (r"\bvenda (agora|ja|tudo)\b", "imperativo de venda"),
    (r"\bhora de (comprar|vender)\b", "call de timing"),
    (r"\bmomento de (comprar|vender)\b", "call de timing"),
    (r"\bfique rico\b", "promessa de enriquecimento"),
    (r"\benriquec\w*", "promessa de enriquecimento"),
    (r"\bdobre seu (dinheiro|capital|patrimonio)\b", "promessa de multiplicação"),
    (r"\bimperdivel\b", "apelo promocional agressivo"),
]

# Frases legítimas removidas antes do lint (o disclaimer usa 'recomendação').
WHITELIST_PATTERNS = [
    r"nao e (uma )?recomendacao( de investimento)?",
    r"sem (tom de )?recomendacao",
    r"nem recomendacao",
]

ALLOWED_RATIOS = {
    "4:5": 1080 / 1350,
    "1:1": 1.0,
    "9:16": 1080 / 1920,
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def lint_text(text: str, source: str) -> list[str]:
    clean = normalize(text)
    for pattern in WHITELIST_PATTERNS:
        clean = re.sub(pattern, " ", clean)
    problems = []
    for pattern, reason in FORBIDDEN_PATTERNS:
        match = re.search(pattern, clean)
        if match:
            problems.append(f"{source}: termo proibido — {reason} (trecho: '{match.group(0)}')")
    return problems


def collect_json_strings(value) -> list[str]:
    out = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            out.extend(collect_json_strings(v))
    elif isinstance(value, list):
        for v in value:
            out.extend(collect_json_strings(v))
    return out


def check_png(path: Path) -> list[str]:
    problems = []
    try:
        from PIL import Image
    except Exception:
        print(f"AVISO: Pillow indisponível; validando só a existência de {path.name}.")
        return problems
    with Image.open(path) as img:
        w, h = img.size
        print(f"OK: {path.name} — {w}x{h}")
        if w < 1080:
            problems.append(f"{path.name}: largura {w} < 1080.")
        ratio = w / h
        if not any(abs(ratio - r) < 0.01 for r in ALLOWED_RATIOS.values()):
            problems.append(
                f"{path.name}: proporção {ratio:.3f} fora dos formatos aceitos (4:5, 1:1, 9:16)."
            )
    return problems


def check_copy(path: Path) -> list[str]:
    problems = []
    text = path.read_text(encoding="utf-8")
    if len(text.strip()) < 80:
        problems.append(f"{path.name}: copy muito curta ou vazia.")
    if normalize(DISCLAIMER_MARKER) not in normalize(text):
        problems.append(f"{path.name}: falta o disclaimer padrão ('Não é recomendação de investimento').")
    hashtags = re.findall(r"(?<!\w)#\w+", text)
    if len(hashtags) > 4:
        problems.append(f"{path.name}: {len(hashtags)} hashtags (máximo 4).")
    problems.extend(lint_text(text, path.name))
    if not problems:
        print(f"OK: {path.name} — copy válida ({len(hashtags)} hashtags)")
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    problems: list[str] = []
    saw_png = saw_copy = False

    for item in argv:
        path = Path(item)
        if not path.exists():
            problems.append(f"NÃO ENCONTRADO: {path}")
            continue
        suffix = path.suffix.lower()
        if suffix == ".png":
            saw_png = True
            problems.extend(check_png(path))
        elif suffix in {".md", ".txt"}:
            saw_copy = True
            problems.extend(check_copy(path))
        elif suffix == ".json":
            spec = json.loads(path.read_text(encoding="utf-8"))
            blob = "\n".join(collect_json_strings(spec))
            json_problems = lint_text(blob, path.name)
            problems.extend(json_problems)
            if not json_problems:
                print(f"OK: {path.name} — config sem termos proibidos")
        else:
            print(f"OK: {path.name} — {path.stat().st_size} bytes")

    if not saw_png:
        problems.append("Nenhum PNG informado — a entrega exige a imagem final.")
    if not saw_copy:
        problems.append("Nenhuma copy (.md) informada — a entrega exige a copy final.")

    if problems:
        print("\nFALHAS:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("\nEntrega válida: imagem + copy dentro do padrão.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

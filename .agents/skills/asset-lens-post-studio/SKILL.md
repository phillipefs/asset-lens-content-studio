---
name: asset-lens-post-studio
description: "Cria posts, stories e carrosseis premium do Asset Lens para Instagram. Use quando o usuario pedir arte, post, copy, legenda, carrossel, story, campanha de conversao ou publicacao baseada em screenshot do produto. Sempre renderiza PNG final, escreve copy.md e valida compliance e qualidade visual."
compatibility: "Requer Python 3.10+ e Google Chrome ou Microsoft Edge local. Funciona em Claude Code, Codex e GitHub Copilot por meio do padrao Agent Skills."
metadata:
  author: "Asset Lens"
  version: "1.0.0"
argument-hint: "[tema ou caminho de screenshot] + [mensagem principal opcional] + [formato opcional]"
allowed-tools: "Read Write Edit Glob Bash(python *) Bash(python3 *)"
disable-model-invocation: false
user-invocable: true
---

# Asset Lens Post Studio

## Contrato de entrega (inegociável)

Todo pedido termina com estes arquivos **existindo e verificados** em
`instagram/AAAA-MM-DD-<slug>/` na raiz do projeto:

1. `post.png` (ou `slide-01.png` … `slide-NN.png` em carrossel);
2. `copy.md` com a legenda final.

Nunca encerrar entregando apenas conceito, prompt, roteiro ou estrutura.
Nunca afirmar que um arquivo foi criado sem tê-lo verificado.

## Contexto obrigatório

Antes de escrever a mensagem, ler:

- [posicionamento e limites do produto](./references/product-brief.md);
- [regras editoriais e regulatórias](./references/compliance.md);
- [voz, pilares e CTAs](./references/messaging.md).

Para citar funcionalidades, consultar o
[catálogo de recursos](./references/feature-catalog.md). O
[snapshot atual](./references/current-snapshot.md) só pode fundamentar números
quando a peça informar a data ou quando o dado tiver sido reconfirmado em uma
fonte atual. Nunca transformar um snapshot em promessa permanente.

## Fluxo obrigatório

### 1. Ler as referências visuais

- Listar `references/approved_examples/` e ler **TODOS** os exemplos
  aprovados (não só um). Cada um ensina um padrão diferente — analise o conjunto
  antes de escolher o layout.
- Papel de cada referência:
  - `post-aprovado-drawdown.png` / `carrossel-aprovado-02-drawdown.png` →
    **screenshot real do produto grande e legível** + cards numerados.
  - `carrossel-aprovado-01-capa.png` → cards de feature numerados lado a lado.
  - `carrossel-aprovado-03-setores.png` → painel real de setores (cards).
  - `carrossel-aprovado-04-ciclos.png` / `-05-ocorrencias.png` → painel/tabela
    real do produto + tiles de KPI.
- Consultar o [guia de marca](./brand_guide.md) e o
  [padrão de qualidade](./QUALITY_STANDARD.md).
- Precedência em conflito: `approved_examples` (o conjunto) > regra genérica >
  preferência do renderizador.
- Atenção: exemplos antigos exibem a marca antiga "Asset Lens Data". O estilo
  vale como referência; o **nome e o logo nunca** — ver Identidade abaixo.

### 2. Criar a pasta do post

- Raiz do projeto: ancestral que contém `studio.config.json`; depois variáveis
  `ASSET_LENS_PROJECT_ROOT`/`CLAUDE_PROJECT_DIR`; Git é apenas fallback.
- Pasta: `instagram/AAAA-MM-DD-<slug-curto-do-tema>/` (ex.:
  `instagram/2026-07-19-drawdown-historico/`). Nunca sobrescrever pasta de
  outro post; se já existir, acrescentar sufixo (`-b`, `-c`).

### 3. Montar o `render.json` dentro da pasta do post

Schema (campos opcionais podem ser omitidos):

```json
{
  "mode": "post | carousel",
  "format": "feed_4x5 | square | story_9x16",
  "output_dir": "instagram/2026-07-19-drawdown-historico",
  "filename": "post.png",
  "eyebrow": "DRAWDOWN POR ATIVO",
  "eyebrow_icon": "grid | pin | search | ...",
  "headline_lines": [
    {"text": "Quedas fazem parte", "color": "white"},
    {"text": "do histórico.", "color": "cyan"}
  ],
  "subtitle": "Uma frase objetiva de apoio, sem promessa.",
  "chips": [
    {"icon": "trend-down", "text": "Picos de drawdown"},
    {"icon": "target", "text": "Faixas quantitativas"}
  ],
  "visual": {"type": "screenshot | steps | stats | sectors | drawdown | cycles | none"},
  "cta": "Veja o drawdown de cada ativo",
  "cta_secondary": "Acompanhe o lançamento",
  "disclaimer": "Conteúdo informacional. Não é recomendação de investimento.",
  "watermark": "auto | always | off",
  "slides": [{"...": "em modo carousel, um objeto por slide; campos comuns fora"}]
}
```

Diretrizes de composição:

- Headline: 2–3 linhas, última linha (ou a palavra-chave) em `cyan` ou `teal`;
  o corpo é ajustado automaticamente.
- Chips: 2–4, curtos. Ícones disponíveis: `search`, `shield`, `shield-check`,
  `trend-down`, `trend-up`, `cycle`, `pie`, `bars`, `clock`, `layers`,
  `target`, `grid`, `pin`, `user`, `zoom` (omitindo `icon`, é inferido do texto).
- **Escolha do visual pelo tema (não use gráfico de linha por padrão):**
  - `screenshot` → **preferir sempre que o tema tiver tela correspondente** e
    houver imagem real (drawdown, matriz, setores, ciclos, painel). É o hero.
  - `steps` → "como funciona"/features: 2–4 cards numerados
    (`items: [{icon, title, desc, color?}]`).
  - `stats` → números em contexto: 3–6 tiles de KPI
    (`items: [{value, label, sub?, color?}]`; `value` é string já formatada).
  - `sectors` → leitura por setores (`items: [{name, value, sub?, color?}]`).
  - `drawdown` → quedas/faixas P75/P90/P95 (`values`, `levels`, `x_labels`).
  - `cycles` → **apenas série temporal real** (preço, ciclos, evolução no
    tempo); `series: [{label, color, values}]`, `baseline_*`.
  - `none` → painel vazio (raro).
- Regra: **gráfico de linha (`cycles`/`drawdown`) só quando o assunto é uma série
  ao longo do tempo.** Para features use `steps`; para números `stats`; para o
  produto `screenshot`. Varie os layouts entre os posts de um mesmo conjunto.
- Todos aceitam `panel_title`/`panel_title_right`. Sem screenshot os elementos
  são **conceituais**: nunca inventar números que pareçam dados reais do produto
  (marque como "ilustrativo"/"exemplo" quando forem hipotéticos). Ver `README.md`.

### 4. Cenários

**A. Screenshot da plataforma (preferencial p/ temas com tela)** — sempre que o
tema tiver uma tela correspondente do produto, prefira a imagem real:

- Usar o caminho real do arquivo em
  `visual: {"type": "screenshot", "screenshot_path": "C:/caminho/real.png"}`.
  Se a imagem veio como anexo sem caminho em disco, **pedir o arquivo antes**.
- O screenshot real é o protagonista e agora **preenche o painel** (grande e
  legível): preservar textos, números e gráficos; proibido recriar a interface,
  substituí-la por cards sintéticos ou deixá-la pequena.
- **Recorte a imagem no essencial** antes de usar (sem grandes margens/áreas
  vazias) para que o conteúdo do produto ocupe o painel.
- Inset de detalhe: **desligado por padrão** (o hero já é grande). Para destacar
  um ponto, ligue com
  `visual.detail = {"x": 82, "y": 14, "zoom": 2.4, "label": "Distribuição por zona"}`
  (`x`/`y` = centro do ponto de interesse em % da imagem).
- Screenshots devem ser nítidos: capturar em `--force-device-scale-factor=2`.

**B. Tema sem imagem** — escolher o visual pelo tema (§3): `steps` para
features/"como funciona", `stats` para números em contexto, `sectors` para
leitura setorial, `drawdown` para quedas/faixas, `cycles` **apenas** para série
temporal real. **Não** caia no gráfico de linha por padrão. Compor dados
conceituais que contem a história do tema, sem inventar dados que pareçam reais.

**C. Carrossel** — `mode: "carousel"`, um objeto por slide em `slides`, campos
comuns (formato, disclaimer) fora. Cada slide tem uma única mensagem; o CTA
dos slides intermediários aponta para o próximo ("Deslize", "Siga"). Uma única
`copy.md` para o carrossel inteiro.

### 5. Renderizar

```powershell
python ".agents/skills/asset-lens-post-studio/scripts/run.py" --config "instagram/<pasta>/render.json"
```

O script localiza Chrome/Edge, captura em 2x e entrega o PNG final no tamanho
correto. Se falhar: ler o erro, corrigir o `render.json` e rodar de novo.

### 6. Escrever a `copy.md` (sempre, mesmo sem pedido explícito)

Estrutura: hook (1 linha) → contexto objetivo (2–4 linhas) → o que o leitor
consegue observar no Asset Lens (leitura quantitativa, sem promessa) → CTA →
disclaimer → até **4** hashtags.

Vocabulário:

- **Proibido**: "ganhe", "lucro/lucre/lucrar", "oportunidade garantida",
  "garantido(a)", "sinal de compra", "sinal de venda", "recomendo/recomendamos/
  recomendação de compra ou venda", "preço-alvo", "compre", "venda agora",
  "hora/momento de comprar ou vender", "fique rico", "enriqueça", qualquer
  promessa de retorno ou aconselhamento de investimento.
- **Preferido**: "leitura quantitativa", "métricas históricas", "faixas
  quantitativas", "risco", "ciclos", "contexto", "acompanhamento",
  "histórico", "informacional".
- Disclaimer obrigatório na arte e na copy:
  `Conteúdo informacional. Não é recomendação de investimento.`

### 7. Verificar (obrigatório)

```powershell
python ".agents/skills/asset-lens-post-studio/scripts/verify_output.py" instagram/<pasta>/post.png instagram/<pasta>/copy.md instagram/<pasta>/render.json
```

Valida existência, proporção, disclaimer, limite de hashtags e o lint de
termos proibidos. Falhou → corrigir e repetir.

### 8. Auto-revisão visual (obrigatória)

1. `Read` no PNG gerado.
2. Comparar com o **conjunto** de `approved_examples/` (não só o benchmark),
   usando o checklist de `QUALITY_STANDARD.md`:
   - mesma família visual (fundo, glow, glass, hierarquia), marca correta;
   - **enquadramento e legibilidade**: screenshot/elementos preenchem o painel e
     são legíveis (não minúsculos nem cercados de margem vazia); nada essencial
     ilegível na miniatura; headline não cortada; painel não é maioria vazio;
   - **variedade**: a peça não é "mais um gráfico de linha" quando o tema não é
     série temporal.
3. Reprovou em algo → ajustar `render.json` (visual, dados, recorte do
   screenshot) e **re-renderizar**. Máximo de 3 iterações; persistindo, entregar
   a melhor versão e relatar a limitação honestamente.

### 9. Resposta final

```text
Imagem: instagram/2026-07-19-drawdown-historico/post.png
Copy:   instagram/2026-07-19-drawdown-historico/copy.md
Validação: verify_output OK; revisão visual vs approved_examples OK (N iterações).
```

## Identidade oficial

- Nome: exatamente `Asset Lens`. **Nunca** "Asset Lens Data" — nem quando uma
  referência antiga mostrar o nome antigo.
- Logo: [logo oficial](./references/brand/logo_official.png) (alpha preservado, sem caixa
  preta, sem redesenho, sem ícone genérico). O renderizador aplica no header.
- Paleta e assinatura visual: ver o [guia de marca](./brand_guide.md). Fundo escuro navy premium;
  não clarear além das referências; sem grid quadriculado por padrão.
- Marca d'água "A" (`watermark`): `auto` usa em posts conceituais de feed e
  desliga em story e screenshot; manter sutil e secundária.

## Formatos

| Formato | Uso | Tamanho final |
|---|---|---|
| `feed_4x5` (padrão) | post de feed | 1080×1350 |
| `square` | feed quadrado | 1080×1080 |
| `story_9x16` | story/reel | 1080×1920 |
| carrossel | N slides `feed_4x5` + `copy.md` única | 1080×1350 cada |

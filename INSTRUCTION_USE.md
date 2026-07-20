# Manual de Uso — Asset Lens Post Studio

Este manual explica como extrair o máximo da skill `asset-lens-post-studio` em
Claude Code, Codex e GitHub Copilot. Ele cobre todas as famílias de recursos
suportadas pelo motor atual e exemplos representativos das combinações
possíveis.

> Regra central: toda execução de produção deve terminar com imagem final PNG,
> `copy.md`, `render.json`, verificação automática e revisão visual.

## 1. O que a skill entrega

A skill pode criar:

- post vertical de feed em 1080×1350;
- post quadrado em 1080×1080;
- story/reel cover em 1080×1920;
- carrossel com qualquer quantidade prática de slides 1080×1350;
- arte baseada em screenshot real da plataforma;
- arte conceitual sem screenshot;
- cards numerados de funcionalidades;
- tiles de métricas/KPIs;
- painel conceitual por setores;
- gráfico de drawdown/faixas;
- gráfico de ciclos/série temporal;
- publicação de lançamento, educação, conversão ou crescimento de seguidores;
- legenda completa com CTA, disclaimer e até quatro hashtags;
- HTML intermediário para depuração;
- validação de dimensões, copy, disclaimer, hashtags e termos proibidos.

Arquivos finais de um post:

```text
instagram/YYYY-MM-DD-slug/
├── post.png
├── copy.md
├── render.json
└── render.html
```

Arquivos finais de um carrossel:

```text
instagram/YYYY-MM-DD-slug-carrossel/
├── slide-01.png
├── slide-02.png
├── slide-NN.png
├── copy.md
├── render.json
├── render-01.html
├── render-02.html
└── render-NN.html
```

## 2. Preparação inicial

Abra **esta pasta como workspace independente** no VS Code:

```text
C:\Python_Projetos\asset-lens-content-studio
```

Instale os requisitos:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts\validate_studio.py
```

Também é necessário ter Google Chrome ou Microsoft Edge instalado.

## 3. Como invocar em cada agente

### Claude Code

```text
/asset-lens-post-studio Crie um post sobre drawdown histórico, formato feed 4:5.
```

### Codex

```text
$asset-lens-post-studio Crie um post sobre drawdown histórico, formato feed 4:5.
```

Também é possível abrir `/skills` e selecionar `asset-lens-post-studio`.

### GitHub Copilot

```text
/asset-lens-post-studio Crie um post sobre drawdown histórico, formato feed 4:5.
```

### Invocação implícita

A skill também pode ser escolhida automaticamente quando o pedido contiver
termos como:

- post do Asset Lens;
- arte para Instagram;
- carrossel;
- story;
- legenda/copy;
- publicação de conversão;
- post usando screenshot da plataforma.

Para máxima previsibilidade, prefira a invocação explícita.

## 4. Estrutura do prompt ideal

Um pedido forte informa oito elementos:

1. **Objetivo** — seguidores, educação, lançamento, conversão ou retenção.
2. **Público** — investidor autodirigido, iniciante, analítico, aportador etc.
3. **Mensagem** — uma única ideia central.
4. **Formato** — feed, square, story ou carrossel.
5. **Recurso real** — zonas, setores, drawdown, ciclos, mudanças etc.
6. **Screenshot** — caminho em disco, quando houver.
7. **CTA** — seguir, salvar, acompanhar ou conhecer.
8. **Referência visual** — exemplo aprovado prioritário, se desejar.

Modelo para copiar:

```text
/asset-lens-post-studio

Objetivo: [crescimento / educação / conversão / lançamento].
Público: [quem deve se identificar].
Formato: [feed_4x5 / square / story_9x16 / carrossel com N slides].
Mensagem principal: [uma frase].
Recurso do produto: [zonas / drawdown / setores / ciclos / mudanças / matriz].
Screenshot: [caminho absoluto ou "não tenho"].
CTA: [ação desejada].
Referência prioritária: [nome do approved example].
Restrições: linguagem informacional, sem indicação de operação.

Entregue PNG final + copy.md + render.json, execute verify_output e revise
visualmente contra todos os approved examples.
```

## 5. Prompt fraco versus prompt forte

### Fraco

```text
Faça um post de investimentos.
```

Esse pedido deixa objetivo, público e mensagem em aberto. A skill ainda pode
produzir algo, mas o resultado tende a ser genérico.

### Forte

```text
/asset-lens-post-studio Crie um post feed 4:5 para investidores que fazem
aportes mensais. A mensagem é: antes de decidir, compare cada ativo com o
próprio histórico. Use cards numerados inspirados no
carrossel-aprovado-01-capa.png. CTA para salvar e acompanhar o Asset Lens.
Sem números hipotéticos que pareçam reais e sem linguagem de compra/venda.
```

## 6. Como escolher o visual

| Necessidade | `visual.type` recomendado |
|---|---|
| Mostrar tela real do produto | `screenshot` |
| Explicar recursos ou processo | `steps` |
| Destacar números reais ou conceitos mensuráveis | `stats` |
| Comparar grupos/setores | `sectors` |
| Explicar queda e faixas P75/P90/P95 | `drawdown` |
| Mostrar evolução ou ciclos no tempo | `cycles` |
| Layout sem painel interno | `none` |

Regras práticas:

- existe tela real correspondente? Use `screenshot`;
- é uma lista de benefícios? Use `steps`;
- a história depende de números? Use `stats`;
- a história compara setores? Use `sectors`;
- a história é uma queda ao longo do tempo? Use `drawdown`;
- a história é uma série temporal real? Use `cycles`;
- nunca use gráfico de linha apenas para preencher espaço.

## 7. Exemplos de prompts sem screenshot

Sem screenshot, a skill cria uma arte contextual com cards, tiles ou gráficos.
Dados hipotéticos devem ser identificados como ilustrativos.

### 7.1 Post institucional — visão completa

```text
/asset-lens-post-studio Crie um post feed 4:5 com o gancho "Você acompanha o
preço. Mas entende o ativo inteiro?". Mostre quatro recursos: zonas semanais e
mensais, drawdown, leitura setorial e ciclos históricos. Use visual steps com
quatro cards, inspirado no carrossel-aprovado-01-capa.png. Objetivo: despertar
curiosidade e gerar seguidores. CTA: "Veja além do preço".
```

### 7.2 Post de drawdown

```text
/asset-lens-post-studio Crie um post educativo sobre a diferença entre olhar
uma queda isolada e compará-la com P75, P90 e P95 do próprio ativo. Não tenho
screenshot. Use visual drawdown conceitual, marque o painel como ilustrativo e
não invente números percentuais reais. CTA para salvar o post.
```

### 7.3 Post de setores

```text
/asset-lens-post-studio Crie um post com a mensagem "Seu ativo não se move
sozinho. Olhe o setor.". Use visual sectors com seis grupos conceituais e marque
os valores como ilustrativos. Explique na copy por que a leitura setorial adiciona
contexto. Formato feed 4:5.
```

### 7.4 Post de ciclos históricos

```text
/asset-lens-post-studio Crie um post sobre como um ativo pode reagir de maneiras
diferentes após quedas semelhantes. Use visual cycles somente como série
conceitual, com três trajetórias claramente identificadas como ilustrativas.
Não use retorno como promessa. Formato feed 4:5.
```

### 7.5 Post de métricas/KPIs

```text
/asset-lens-post-studio Crie um post mostrando quais camadas o Asset Lens
organiza: P75/P90/P95, DD 5A, horizontes 1A/2A/3A/5A e MAE 1A. Use visual stats.
Esses textos são nomes de recursos, não resultados de um ativo. Objetivo:
demonstrar profundidade metodológica.
```

### 7.6 Post de metodologia

```text
/asset-lens-post-studio Crie um post "Como o Asset Lens organiza uma leitura".
Use quatro cards: observar a classificação, comparar com o histórico, conectar
setor e mercado, analisar risco. Visual steps. Tom sóbrio e informacional.
```

### 7.7 Post para seguidores

```text
/asset-lens-post-studio Crie um post focado em crescimento de seguidores com o
gancho "Você sabe como seu ativo se comportou ao longo dos anos?". Use um visual
adequado ao tema, CTA explícito para seguir e copy com curiosidade, sem promessa
de resultado.
```

### 7.8 Post de conversão segura

```text
/asset-lens-post-studio Crie um post de alta conversão para o Asset Lens. Venda
clareza, organização e contexto — nunca performance. Gancho: "Menos telas
dispersas. Mais contexto em uma leitura." Use quatro cards de recursos e CTA
"Conheça o Asset Lens".
```

### 7.9 Contexto para aporte mensal

```text
/asset-lens-post-studio Crie um post para quem compara os ativos da carteira
antes do aporte mensal. A plataforma deve aparecer como ferramenta que organiza
evidências históricas, não como sistema que escolhe o ativo. Use zones, drawdown
e histórico em cards. CTA: "Compare com contexto histórico".
```

### 7.10 Mudanças de classificação

```text
/asset-lens-post-studio Crie um post educativo sobre acompanhar mudanças de
classificação entre execuções do painel. Use visual steps: o que mudou hoje,
o que mudou na semana, faixas próximas dos limiares e consulta na matriz.
Não use a palavra sinal.
```

## 8. Exemplo usando screenshot real da plataforma

### 8.1 Preparar o arquivo

Anexo de chat não é automaticamente um arquivo acessível ao renderizador.
Salve primeiro o print em:

```text
inputs/screenshots/YYYY-MM-DD-descricao.png
```

Crie um arquivo adjacente com origem e data:

```text
inputs/screenshots/YYYY-MM-DD-descricao.md
```

O screenshot deve:

- estar recortado no componente importante;
- preservar dados e interface;
- evitar grandes margens vazias;
- preferencialmente ter sido capturado em 2x;
- não conter e-mail, credencial ou dado pessoal;
- ter autorização de uso.

### 8.2 Prompt com screenshot

```text
/asset-lens-post-studio Crie um post feed 4:5 sobre a leitura macro dos ativos
por zonas. Use obrigatoriamente o screenshot real:
C:\Python_Projetos\asset-lens-content-studio\inputs\screenshots\2026-07-20-zonas-app.png

O screenshot deve ser o protagonista, grande e legível. Inspire-se no
carrossel-aprovado-02-drawdown.png. Gancho: "O mercado inteiro em uma leitura
por zonas". CTA para seguir o Asset Lens. Identifique os números como snapshot
de 20/07/2026.
```

### 8.3 Prompt com detalhe ampliado

```text
/asset-lens-post-studio Use o screenshot abaixo como hero e adicione um inset de
detalhe sobre a região da Zona Neutra:
C:\caminho\painel-zonas.png

Centro aproximado do detalhe: x=70%, y=58%, zoom=2.3. Label: "Concentração na
Zona Neutra". Formato feed 4:5. Preserve todos os dados originais.
```

### 8.4 Prompt com screenshot de drawdown

```text
/asset-lens-post-studio Crie um post educativo usando este screenshot real do
modal de drawdown: C:\caminho\drawdown-ativo.png. A mensagem é "Uma queda ganha
significado quando comparada ao próprio histórico". Não reproduza o gráfico
manualmente; use a imagem real em destaque. CTA para salvar.
```

### 8.5 Prompt com screenshot de setores

```text
/asset-lens-post-studio Crie um post usando este print real do painel setorial:
C:\caminho\setores.png. Destaque que o ativo deve ser lido dentro do grupo,
sem concluir qual setor é preferível. Inspire-se no
carrossel-aprovado-03-setores.png.
```

## 9. Exemplos de carrossel

### 9.1 Carrossel sem screenshot

```text
/asset-lens-post-studio Crie um carrossel de 5 slides sobre "O que o preço
isolado não mostra".

Slide 1: capa com o gancho.
Slide 2: zonas semanais e mensais.
Slide 3: drawdown e faixas históricas.
Slide 4: setores e mudanças de classificação.
Slide 5: ciclos históricos + CTA para seguir.

Use layouts variados entre steps e stats. Uma única copy.md. CTAs intermediários
devem indicar "Deslize". Sem números que pareçam dados atuais.
```

### 9.2 Carrossel com screenshot real

```text
/asset-lens-post-studio Crie um carrossel de 5 slides sobre classificação por
zonas.

Slide 1: capa inspirada no carrossel-aprovado-01-capa.png.
Slide 2: explique as quatro zonas com cards numerados.
Slide 3: use como hero o screenshot real
C:\caminho\zonas_app.png.
Slide 4: explique como ler as zonas como contexto, não como ordem de operação.
Slide 5: resumo e CTA para seguir.

Use uma única copy.md e mantenha o disclaimer em todos os slides.
```

### 9.3 Carrossel de drawdown

```text
/asset-lens-post-studio Crie um carrossel de 4 slides inspirado no
carrossel-aprovado-02-drawdown.png.

1. Por que uma queda isolada engana.
2. Screenshot real do drawdown do produto: C:\caminho\drawdown.png.
3. O papel das faixas P75, P90 e P95.
4. Como usar o histórico como contexto + CTA.

Não use números de retorno como headline.
```

### 9.4 Carrossel de recursos do produto

```text
/asset-lens-post-studio Crie um carrossel de lançamento com 6 slides:
capa, visão macro, setores, matriz por ativo, drawdown, ciclos históricos e CTA
final. Explore o máximo de recursos do catálogo, mas mantenha uma mensagem por
slide. Use screenshot real quando houver arquivo em inputs/screenshots/.
```

### 9.5 Carrossel de mito versus contexto

```text
/asset-lens-post-studio Crie um carrossel de 5 slides no formato
"percepção comum versus leitura quantitativa".

Não use tom de confronto. Exemplos: "caiu muito" versus drawdown histórico;
"está barato" versus faixa do próprio ativo; "o setor está igual" versus leitura
setorial. Finalize lembrando que contexto não é recomendação.
```

## 10. Story e formato quadrado

### 10.1 Story 9:16

```text
/asset-lens-post-studio Crie um story 1080×1920 sobre "Dados, não dicas".
Use headline curta, dois chips, visual steps com no máximo três itens e CTA para
acompanhar o lançamento. Não use marca d'água. Garanta leitura em tela de celular.
```

### 10.2 Story com screenshot

```text
/asset-lens-post-studio Crie um story 9:16 com o screenshot
C:\caminho\painel.png. O print deve ocupar o painel principal sem ficar
minúsculo. Reduza a quantidade de texto e use CTA curto.
```

### 10.3 Post quadrado

```text
/asset-lens-post-studio Crie uma versão square 1080×1080 do conceito "Leia a
queda com referência". Use headline de duas linhas, visual stats com três tiles
e copy completa. Verifique se o conteúdo compacto não foi cortado.
```

## 11. Produção em lote e variações

### 11.1 Três posts com ângulos diferentes

```text
/asset-lens-post-studio Crie 3 posts separados, cada um em sua própria pasta:

1. Contexto além do preço — visual steps.
2. Queda com referência — visual stats ou drawdown.
3. Mercado em grupos — visual sectors.

Cada post deve ter gancho, CTA e copy próprios. Varie os layouts e valide todos.
```

### 11.2 Variações A/B

```text
/asset-lens-post-studio Crie duas versões do mesmo tema em pastas diferentes.
Versão A: gancho em forma de pergunta. Versão B: afirmação contrarian sóbria.
Mantenha o mesmo recurso do produto e CTA. Não sobrescreva nenhuma pasta.
```

### 11.3 Adaptar post existente

```text
/asset-lens-post-studio Leia
instagram/2026-07-20-tema/render.json e crie uma nova variação em outra pasta.
Preserve a identidade, troque o gancho e use outro visual adequado. Não altere
a entrega original.
```

### 11.4 Criar a partir de um brief

```text
/asset-lens-post-studio Siga integralmente o brief em
briefs/2026-07-20-campanha.md. Quando houver conflito, respeite compliance,
marca e approved examples. Entregue e valide todos os arquivos.
```

## 12. Referência completa do `render.json`

### 12.1 Campos gerais

| Campo | Tipo | Uso |
|---|---|---|
| `mode` | string | `post` ou `carousel` |
| `format` | string | `feed_4x5`, `square`, `story_9x16` |
| `output_dir` | string | pasta de saída relativa à raiz |
| `filename` | string | nome do PNG em post único |
| `project_root` | string | override explícito de raiz, raramente necessário |
| `eyebrow` | string | selo superior em caixa alta |
| `eyebrow_icon` | string | ícone do selo |
| `headline_lines` | array | até três linhas com texto e cor |
| `headline_size` | número | tamanho inicial; o motor ainda reduz para caber |
| `subtitle` | string | apoio objetivo |
| `chips` | array | até quatro chips |
| `visual` | objeto | painel principal |
| `cta` | string | chamada principal |
| `cta_secondary` | string | linha secundária opcional |
| `disclaimer` | string | obrigatório |
| `watermark` | string | `auto`, `always` ou `off` |
| `watermark_letter` | string | letra opcional da marca d'água |
| `outer_frame` | boolean | moldura externa opcional |
| `layout` | string | `hero` compacta margens para ampliar o painel |
| `brand_logo_path` | string | override de logo; evitar sem aprovação de marca |
| `slides` | array | objetos de slide no modo carousel |

Compatibilidade legada:

- `headline` vira uma linha de headline;
- `features` vira chips com ícones inferidos;
- `background_monogram_mode` vira `watermark`.

Prefira sempre os campos atuais.

### 12.2 Cores disponíveis

```text
white
cyan
teal
blue
green
yellow
red
```

Também é aceito hexadecimal, por exemplo `#22D8F4`. Use vermelho e amarelo
somente em indicadores de risco, faixas ou métricas.

### 12.3 Ícones disponíveis

```text
search
shield
shield-check
trend-down
trend-up
cycle
pie
bars
clock
layers
target
grid
pin
user
zoom
```

Quando o ícone do chip é omitido, o motor tenta inferi-lo pelo texto.

## 13. Configuração completa de post conceitual

```json
{
  "mode": "post",
  "format": "feed_4x5",
  "output_dir": "instagram/YYYY-MM-DD-contexto-historico",
  "filename": "post.png",
  "eyebrow": "LEITURA QUANTITATIVA",
  "eyebrow_icon": "search",
  "headline_lines": [
    {"text": "Antes de decidir,", "color": "white"},
    {"text": "compare com", "color": "white"},
    {"text": "o próprio histórico.", "color": "cyan"}
  ],
  "subtitle": "Zonas, risco e ciclos organizados em uma leitura informacional.",
  "chips": [
    {"icon": "target", "text": "Zonas quantitativas"},
    {"icon": "trend-down", "text": "Drawdown"},
    {"icon": "clock", "text": "Contexto histórico"}
  ],
  "visual": {
    "type": "steps",
    "panel_title": "CAMADAS DA LEITURA",
    "panel_title_right": "informacional",
    "items": [
      {"icon": "search", "title": "Observe", "desc": "Leia a classificação atual.", "color": "cyan"},
      {"icon": "clock", "title": "Compare", "desc": "Consulte ocorrências históricas.", "color": "teal"},
      {"icon": "layers", "title": "Conecte", "desc": "Relacione ativo, setor e mercado.", "color": "blue"},
      {"icon": "shield-check", "title": "Contextualize", "desc": "A decisão permanece autônoma.", "color": "green"}
    ]
  },
  "cta": "Acompanhe o Asset Lens",
  "cta_secondary": "Dados, não dicas.",
  "disclaimer": "Conteúdo informacional. Não é recomendação de investimento.",
  "watermark": "auto"
}
```

## 14. Configuração de cada visual

### 14.1 `steps`

Use de dois a quatro cards. Com três itens, os cards ficam lado a lado; com
quatro, formam grade 2×2.

```json
{
  "type": "steps",
  "panel_title": "COMO FUNCIONA",
  "items": [
    {"icon": "trend-down", "title": "Veja a queda", "desc": "Meça a distância da máxima.", "color": "cyan"},
    {"icon": "target", "title": "Compare faixas", "desc": "Consulte P75, P90 e P95.", "color": "teal"},
    {"icon": "clock", "title": "Leia o histórico", "desc": "Observe ocorrências anteriores.", "color": "blue"},
    {"icon": "shield-check", "title": "Mantenha autonomia", "desc": "Use como contexto informacional.", "color": "green"}
  ]
}
```

### 14.2 `stats`

Aceita até seis tiles. `value` é uma string já formatada.

```json
{
  "type": "stats",
  "panel_title": "MÉTRICAS DISPONÍVEIS",
  "panel_title_right": "recursos do produto",
  "items": [
    {"value": "P75·P90·P95", "label": "Faixas históricas", "sub": "referências do próprio ativo", "color": "yellow"},
    {"value": "DD 5A", "label": "Queda desde o pico", "sub": "janela recente", "color": "red"},
    {"value": "1A·2A·3A·5A", "label": "Horizontes", "sub": "quando há dados suficientes", "color": "cyan"},
    {"value": "MAE 1A", "label": "Percurso adverso", "sub": "métrica histórica", "color": "blue"}
  ]
}
```

### 14.3 `sectors`

Aceita até seis grupos. `value` deve ser numérico entre 0 e 100 para definir a
largura da barra. O valor exibido pode receber `value_suffix`.

```json
{
  "type": "sectors",
  "panel_title": "LEITURA POR SETORES",
  "panel_title_right": "ilustrativo",
  "value_suffix": "",
  "value_label": "índice ilustrativo",
  "items": [
    {"name": "Financeiro", "value": 62, "sub": "exemplo conceitual", "color": "green"},
    {"name": "Utilidades", "value": 55, "sub": "exemplo conceitual", "color": "yellow"},
    {"name": "Materiais", "value": 49, "sub": "exemplo conceitual", "color": "blue"},
    {"name": "Tecnologia", "value": 43, "sub": "exemplo conceitual", "color": "cyan"}
  ]
}
```

### 14.4 `drawdown`

`values` e `frac` usam posições normalizadas de 0 a 1. Se não forem dados reais
transformados de forma consistente, marque o painel como ilustrativo.

```json
{
  "type": "drawdown",
  "panel_title": "DRAWDOWN — CONCEITO",
  "panel_title_right": "ilustrativo",
  "values": [0.06, 0.14, 0.24, 0.16, 0.50, 0.74, 0.56, 0.40, 0.63, 0.44, 0.30, 0.20],
  "levels": [
    {"label": "P75", "frac": 0.36, "color": "blue"},
    {"label": "P90", "frac": 0.52, "color": "yellow"},
    {"label": "P95", "frac": 0.66, "color": "red"}
  ],
  "x_labels": ["início", "ciclo 1", "ciclo 2", "hoje"],
  "legend": ["Distância da máxima", "Faixas quantitativas"]
}
```

### 14.5 `cycles`

Use somente para série temporal. `values` são posições normalizadas de 0 a 1;
use a mesma transformação para todas as séries.

```json
{
  "type": "cycles",
  "panel_title": "COMPORTAMENTO AO LONGO DO TEMPO",
  "panel_title_right": "ilustrativo",
  "baseline_frac": 0.30,
  "baseline_label": "topo do ciclo",
  "series": [
    {"label": "Trajetória A", "color": "cyan", "values": [0.30, 0.31, 0.44, 0.36, 0.24, 0.15, 0.10]},
    {"label": "Trajetória B", "color": "teal", "values": [0.30, 0.33, 0.48, 0.55, 0.48, 0.40, 0.34]},
    {"label": "Trajetória C", "color": "blue", "values": [0.30, 0.36, 0.62, 0.84, 0.72, 0.62, 0.55]}
  ]
}
```

### 14.6 `screenshot`

```json
{
  "type": "screenshot",
  "screenshot_path": "C:/caminho/real/painel.png",
  "caption": "Snapshot da plataforma"
}
```

Com detalhe:

```json
{
  "type": "screenshot",
  "screenshot_path": "C:/caminho/real/painel.png",
  "detail": {
    "x": 72,
    "y": 35,
    "zoom": 2.4,
    "label": "Detalhe do painel"
  }
}
```

`x` e `y` indicam o centro do ponto de interesse em porcentagem da imagem.

### 14.7 `none`

```json
{
  "type": "none",
  "panel_title": ""
}
```

Use raramente. Um painel sem conteúdo pode deixar a peça visualmente vazia.

## 15. Configuração completa de carrossel

```json
{
  "mode": "carousel",
  "format": "feed_4x5",
  "output_dir": "instagram/YYYY-MM-DD-contexto-carrossel",
  "watermark": "off",
  "disclaimer": "Conteúdo informacional. Não é recomendação de investimento.",
  "slides": [
    {
      "filename": "slide-01.png",
      "eyebrow": "ALÉM DO PREÇO",
      "eyebrow_icon": "search",
      "headline_lines": [
        {"text": "O que o preço", "color": "white"},
        {"text": "isolado não mostra?", "color": "cyan"}
      ],
      "subtitle": "Quatro camadas para adicionar contexto à leitura.",
      "visual": {
        "type": "steps",
        "items": [
          {"icon": "target", "title": "Zonas", "desc": "Semanal e mensal."},
          {"icon": "trend-down", "title": "Risco", "desc": "Drawdown e faixas."},
          {"icon": "pie", "title": "Setores", "desc": "Contexto do grupo."},
          {"icon": "cycle", "title": "Ciclos", "desc": "Ocorrências históricas."}
        ]
      },
      "cta": "Deslize para continuar"
    },
    {
      "filename": "slide-02.png",
      "eyebrow": "ZONAS",
      "eyebrow_icon": "target",
      "headline_lines": [
        {"text": "Compare o ativo", "color": "white"},
        {"text": "com a própria régua.", "color": "teal"}
      ],
      "visual": {
        "type": "steps",
        "items": [
          {"icon": "grid", "title": "Semanal", "desc": "Leitura mais recente."},
          {"icon": "clock", "title": "Mensal", "desc": "Outro horizonte de contexto."}
        ]
      },
      "cta": "Deslize"
    },
    {
      "filename": "slide-03.png",
      "eyebrow": "NO PRODUTO",
      "eyebrow_icon": "grid",
      "headline_lines": [
        {"text": "A leitura aparece", "color": "white"},
        {"text": "em um painel só.", "color": "cyan"}
      ],
      "visual": {
        "type": "screenshot",
        "screenshot_path": "inputs/screenshots/YYYY-MM-DD-painel.png"
      },
      "cta": "Deslize para o resumo"
    },
    {
      "filename": "slide-04.png",
      "eyebrow": "CONTEXTO",
      "eyebrow_icon": "shield-check",
      "headline_lines": [
        {"text": "Dados organizados.", "color": "white"},
        {"text": "Decisão autônoma.", "color": "green"}
      ],
      "visual": {
        "type": "steps",
        "items": [
          {"icon": "search", "title": "Observe", "desc": "Leia as métricas."},
          {"icon": "clock", "title": "Compare", "desc": "Consulte o histórico."},
          {"icon": "shield-check", "title": "Decida", "desc": "Mantenha autonomia."}
        ]
      },
      "cta": "Siga o Asset Lens",
      "cta_secondary": "Dados, não dicas."
    }
  ]
}
```

O motor acrescenta automaticamente `1/N`, `2/N` etc. quando `slide_number` não
é informado.

## 16. Marca d'água, moldura e layout hero

### Marca d'água

- `auto`: ativa em posts conceituais de feed;
- `always`: força a marca d'água;
- `off`: desativa;
- em story e screenshot, `auto` desativa automaticamente.

```json
{
  "watermark": "always",
  "watermark_letter": "A"
}
```

### Moldura externa

```json
{
  "outer_frame": true
}
```

Use apenas quando combinar com a referência aprovada. Não empilhe molduras sem
necessidade.

### Layout hero

```json
{
  "layout": "hero"
}
```

Reduz margens verticais para ampliar o painel. Screenshots já ativam esse modo
automaticamente.

## 17. Como escrever a copy

Estrutura recomendada:

1. Hook em uma linha.
2. Contexto em dois a quatro parágrafos curtos.
3. O que o leitor consegue observar no produto.
4. CTA.
5. Disclaimer exato.
6. Até quatro hashtags.

Exemplo:

```markdown
Uma queda sem referência parece sempre maior.

O percentual atual é apenas o começo. O que muda a leitura é comparar essa
queda com as faixas e ocorrências do próprio ativo.

No Asset Lens, você observa drawdown, percentis históricos e ciclos em uma
leitura organizada. O objetivo não é prever o próximo movimento, mas ampliar o
contexto disponível.

Salve este post e acompanhe o Asset Lens.

Conteúdo informacional. Não é recomendação de investimento.

#drawdown #risco #investimentos #dados
```

## 18. Compliance: o que evitar

Nunca peça ou aprove:

- promessa de retorno;
- call de compra ou venda;
- preço-alvo;
- ativo garantido;
- urgência artificial;
- afirmação de que a plataforma escolhe o aporte;
- ranking comercial por retorno;
- linguagem de precisão preditiva;
- indicação individualizada.

Reescritas:

| Evite | Prefira |
|---|---|
| sinal | classificação ou leitura |
| entrada | ocorrência histórica |
| taxa de acerto | proporção positiva histórica |
| ganho | variação observada |
| melhor ativo | ativo em determinada faixa |
| oportunidade | caso para análise adicional |
| timing de compra | contexto histórico antes da decisão |

Disclaimer obrigatório:

```text
Conteúdo informacional. Não é recomendação de investimento.
```

## 19. Dados reais versus dados ilustrativos

### Dados reais

Inclua:

- arquivo ou fonte;
- data do snapshot;
- horizonte da métrica;
- contexto suficiente para não parecer promessa.

Prompt:

```text
Use os números deste screenshot como snapshot datado de 20/07/2026. Não diga
que representam o estado atual do mercado. Preserve os valores exatamente.
```

### Dados ilustrativos

Prompt:

```text
Não há dados reais anexados. Crie uma composição conceitual e marque o painel
como "ilustrativo". Não use percentuais ou tickers que possam ser confundidos
com dados atuais do produto.
```

## 20. Renderização manual

Post:

```powershell
python .agents/skills/asset-lens-post-studio/scripts/run.py --config instagram/YYYY-MM-DD-slug/render.json
```

Somente HTML, para depuração:

```powershell
python .agents/skills/asset-lens-post-studio/scripts/run.py --config instagram/YYYY-MM-DD-slug/render.json --html-only
```

Verificação de post:

```powershell
python .agents/skills/asset-lens-post-studio/scripts/verify_output.py instagram/YYYY-MM-DD-slug/post.png instagram/YYYY-MM-DD-slug/copy.md instagram/YYYY-MM-DD-slug/render.json
```

Verificação de carrossel:

```powershell
python .agents/skills/asset-lens-post-studio/scripts/verify_output.py instagram/YYYY-MM-DD-slug/slide-01.png instagram/YYYY-MM-DD-slug/slide-02.png instagram/YYYY-MM-DD-slug/slide-03.png instagram/YYYY-MM-DD-slug/copy.md instagram/YYYY-MM-DD-slug/render.json
```

Validar o estúdio inteiro:

```powershell
python scripts/validate_studio.py
python scripts/smoke_test.py
```

## 21. Variáveis e opções de ambiente

Forçar navegador:

```powershell
$env:ASSET_LENS_BROWSER = "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

Forçar raiz do projeto:

```powershell
$env:ASSET_LENS_PROJECT_ROOT = "C:\caminho\asset-lens-content-studio"
```

Normalmente isso não é necessário porque `studio.config.json` marca a raiz.

## 22. Revisão visual obrigatória

Depois do render, abra cada PNG e confirme:

- nome `Asset Lens` correto;
- logo oficial com transparência;
- fundo navy na mesma família dos aprovados;
- headline legível em miniatura;
- palavra-chave em cyan/teal;
- textos sem cortes;
- cards sem área vazia excessiva;
- screenshot preenchendo o painel;
- números do screenshot legíveis;
- vermelho/amarelo apenas como indicadores;
- CTA equilibrado;
- disclaimer visível;
- visual apropriado ao tema;
- nenhum gráfico de linha usado apenas como decoração.

Se falhar, ajuste e renderize novamente. Limite recomendado: três iterações.

## 23. Solução de problemas

### Skill não aparece no Claude

1. Confirme `.claude/skills/asset-lens-post-studio/SKILL.md`.
2. Reinicie Claude Code se a pasta foi criada após iniciar a sessão.
3. Execute `/asset-lens-post-studio` explicitamente.

### Skill não aparece no Codex

1. Abra o terminal na raiz do projeto.
2. Confirme `.agents/skills/asset-lens-post-studio/SKILL.md`.
3. Use `/skills` ou `$asset-lens-post-studio`.
4. Reinicie o Codex após uma skill recém-criada.

### Skill aparece duplicada no Copilot

Abra esta pasta como workspace e confirme em `.vscode/settings.json`:

```json
{
  "chat.agentSkillsLocations": {
    ".agents/skills": true,
    ".claude/skills": false
  }
}
```

### Screenshot não encontrado

- confirme o caminho em disco;
- prefira barras `/` dentro do JSON;
- para caminho absoluto no Windows, use `C:/pasta/arquivo.png`;
- não passe apenas um anexo de chat sem salvá-lo.

### Chrome/Edge não encontrado

Defina `ASSET_LENS_BROWSER` com o executável real.

### Pillow ausente

```powershell
python -m pip install -r requirements-dev.txt
```

### Headline cortada ou pequena

- reduza palavras;
- distribua em duas ou três linhas;
- evite palavras muito longas;
- ajuste `headline_size` somente depois de simplificar o texto.

### Cards cortados

- reduza o subtítulo;
- remova chips desnecessários;
- use descrições mais curtas;
- prefira quatro cards 2×2 em vez de seis elementos improvisados;
- reabra o PNG depois de cada render.

### Screenshot pequeno dentro do painel

- recorte margens do arquivo original;
- use o componente relevante, não a página inteira;
- remova chips ou subtítulo excessivo;
- use `layout: "hero"` quando necessário.

### Verificador bloqueou a copy

Leia a mensagem do termo proibido, reescreva a frase inteira e execute novamente.
Não tente contornar o lint com grafia alterada.

### Saída foi para a pasta errada

- execute a partir da raiz que contém `studio.config.json`;
- confirme `output_dir` relativo à raiz;
- use `project_root` ou `ASSET_LENS_PROJECT_ROOT` apenas como override.

## 24. Checklist do pedido perfeito

Antes de enviar o prompt, confirme:

- [ ] objetivo definido;
- [ ] público definido;
- [ ] uma mensagem principal;
- [ ] formato definido;
- [ ] quantidade de slides, se carrossel;
- [ ] screenshot salvo em disco, se houver;
- [ ] fonte e data dos números reais;
- [ ] CTA desejado;
- [ ] referência aprovada prioritária;
- [ ] linguagem informacional;
- [ ] pedido explícito de PNG + copy + validação + revisão visual.

## 25. Prompt mestre

Use este prompt quando quiser delegar toda a direção criativa à skill, mas
manter um contrato rigoroso:

```text
/asset-lens-post-studio

Atue como estrategista de conteúdo e designer editorial do Asset Lens.

Objetivo: [objetivo].
Público: [público].
Tema: [tema].
Mensagem principal: [mensagem].
Formato: [formato].
Slides: [quantidade e mensagem de cada slide, se houver].
Screenshot real: [caminho ou "não disponível"].
Dados reais permitidos: [fonte + data ou "nenhum"].
CTA: [CTA].
Referência visual prioritária: [arquivo aprovado].

Leia product-brief, feature-catalog, compliance, messaging, brand_guide,
QUALITY_STANDARD e todos os approved_examples. Escolha o visual adequado ao
tema; não use gráfico de linha por padrão. Se não houver screenshot, use uma
composição conceitual sem inventar dados que pareçam reais.

Crie uma pasta inédita em instagram/YYYY-MM-DD-slug, gere render.json, PNG final
e copy.md. Execute verify_output, abra cada PNG, compare com os exemplos
aprovados e itere até três vezes se houver corte, baixa legibilidade ou
enquadramento ruim. Na resposta final, informe os caminhos e o resultado das
validações.
```

## 26. O que sempre esperar da resposta final

```text
Imagem: instagram/YYYY-MM-DD-slug/post.png
Copy: instagram/YYYY-MM-DD-slug/copy.md
Validação: verify_output OK; revisão visual vs approved_examples OK (N iterações).
```

Para carrossel, a resposta deve listar todos os slides e a copy única.

## 27. Limites atuais do motor

- não gera fotografia externa por IA;
- não busca automaticamente screenshots privados da plataforma;
- não deve reconstruir interface real quando o screenshot está disponível;
- não valida juridicamente uma campanha;
- não transforma dados conceituais em evidência real;
- não publica automaticamente no Instagram;
- não cria vídeo ou animação final;
- não substitui revisão humana de fatos, data e contexto.

Dentro desses limites, todos os visuais, formatos, combinações de slides,
mensagens e CTAs descritos neste manual podem ser combinados para criar novas
publicações.
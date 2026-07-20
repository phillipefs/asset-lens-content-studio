# Asset Lens Content Studio

Repositório focado na criação de posts, stories e carrosséis do Asset Lens. O
projeto mantém contexto suficiente sobre produto, marca e compliance sem levar
o código completo da plataforma para cada sessão.

Para exemplos completos de prompts, screenshots, carrosséis, formatos, visuais,
campos de configuração e troubleshooting, consulte o
[manual de uso](INSTRUCTION_USE.md).

## Requisitos

- Python 3.10 ou superior;
- Google Chrome ou Microsoft Edge;
- Pillow (instalado automaticamente pela skill ou via `requirements-dev.txt`);
- Claude Code, Codex ou GitHub Copilot para execução assistida.

## Preparação

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/validate_studio.py
```

O diretório ainda não é um repositório Git independente. Quando decidir
publicá-lo, execute `git init` manualmente na raiz deste projeto.

## Uso por agente

### Claude Code

```text
/asset-lens-post-studio <tema, screenshot, mensagem e formato>
```

Claude descobre um adaptador em `.claude/skills/` que carrega a skill canônica.

### Codex

```text
$asset-lens-post-studio <tema, screenshot, mensagem e formato>
```

Também é possível selecionar a skill por `/skills`. Codex lê
`.agents/skills/` diretamente.

### GitHub Copilot

```text
/asset-lens-post-studio <tema, screenshot, mensagem e formato>
```

O workspace está configurado para descobrir apenas a versão canônica em
`.agents/skills/`, evitando duplicidade com o adaptador Claude.

## Estrutura

```text
asset-lens-content-studio/
├── AGENTS.md
├── CLAUDE.md
├── studio.config.json
├── .agents/skills/asset-lens-post-studio/   # skill canônica
├── .claude/skills/asset-lens-post-studio/   # adaptador Claude
├── briefs/                                  # pautas de produção
├── inputs/screenshots/                      # capturas reais + metadados
├── instagram/                               # entregas por data/slug
├── templates/                               # briefs e render.json iniciais
├── scripts/                                 # validação e smoke tests
└── tests/fixtures/                          # entradas determinísticas
```

## Fluxo manual

1. Preencha um brief em `briefs/`.
2. Salve screenshots reais em `inputs/screenshots/`.
3. Crie `instagram/YYYY-MM-DD-slug/render.json` e `copy.md`.
4. Renderize:

```powershell
python .agents/skills/asset-lens-post-studio/scripts/run.py --config instagram/YYYY-MM-DD-slug/render.json
```

5. Verifique:

```powershell
python .agents/skills/asset-lens-post-studio/scripts/verify_output.py instagram/YYYY-MM-DD-slug/post.png instagram/YYYY-MM-DD-slug/copy.md instagram/YYYY-MM-DD-slug/render.json
```

6. Abra o PNG e compare com todos os exemplos aprovados.

## Versionamento

`copy.md` e `render.json` são fontes versionáveis. PNGs finais e HTMLs de render
são reproduzíveis e ficam ignorados pelo Git. Screenshots de entrada, logo,
fontes e exemplos aprovados permanecem versionados.

Consulte [o fluxo completo](docs/WORKFLOW.md) e a
[matriz de compatibilidade](docs/AGENT_COMPATIBILITY.md).
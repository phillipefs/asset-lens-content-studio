# Fluxo de Produção

## 1. Abrir a pauta

Use `templates/post-brief.md` ou `templates/carousel-brief.md`. Defina objetivo,
público, mensagem, CTA, formato e qualquer screenshot obrigatório.

## 2. Preparar evidências

- Consulte o catálogo de recursos dentro da skill.
- Confirme números mutáveis em uma fonte datada.
- Salve screenshots em `inputs/screenshots/` com arquivo de metadados adjacente.
- Não use dados pessoais, credenciais ou telas privadas sem autorização.

## 3. Criar a entrega

Crie uma pasta inédita em `instagram/YYYY-MM-DD-slug/`. Use os JSONs de
`templates/` como ponto de partida, não como layout obrigatório.

Cada post exige:

- `render.json`;
- `copy.md`;
- `post.png` ou `slide-01.png` a `slide-NN.png`.

## 4. Renderizar e verificar

```powershell
python .agents/skills/asset-lens-post-studio/scripts/run.py --config instagram/YYYY-MM-DD-slug/render.json
python .agents/skills/asset-lens-post-studio/scripts/verify_output.py instagram/YYYY-MM-DD-slug/post.png instagram/YYYY-MM-DD-slug/copy.md instagram/YYYY-MM-DD-slug/render.json
```

Para carrossel, informe todos os slides ao verificador antes de `copy.md` e
`render.json`.

## 5. Revisar visualmente

Abra cada PNG e confira:

- marca e logo corretos;
- headline legível em miniatura;
- elemento principal ocupando o painel;
- screenshot real sem recriação;
- nenhum corte, sobreposição ou margem vazia excessiva;
- variedade coerente com o tema;
- disclaimer legível.

## 6. Entregar

Informe os caminhos de imagem e copy, resultado do verificador e número de
iterações visuais. Não declare sucesso sem checar os arquivos em disco.

## Comandos por agente

- Claude Code: `/asset-lens-post-studio <brief>`
- Codex: `$asset-lens-post-studio <brief>` ou `/skills`
- GitHub Copilot: `/asset-lens-post-studio <brief>`
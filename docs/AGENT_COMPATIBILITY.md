# Compatibilidade de Agentes

## Estratégia

`.agents/skills/asset-lens-post-studio/` é a única implementação da skill.
Scripts, fontes, exemplos e referências existem somente ali.

| Agente | Descoberta | Entrada |
|---|---|---|
| Codex | `.agents/skills/` | `$asset-lens-post-studio` ou `/skills` |
| GitHub Copilot | `.agents/skills/` via `.vscode/settings.json` | `/asset-lens-post-studio` |
| Claude Code | adaptador em `.claude/skills/` | `/asset-lens-post-studio` |

## Por que não usar symlink

Claude e Codex aceitam skills por symlink, mas links versionados têm diferenças
de permissões e comportamento no Windows. O adaptador Markdown é pequeno,
portável e verificável, sem duplicar binários ou lógica.

## Por que o Copilot ignora `.claude/skills`

VS Code reconhece `.agents/skills` e `.claude/skills`. Como ambas teriam o mesmo
nome, o workspace desabilita a localização de projeto `.claude/skills` para o
Copilot. Skills pessoais continuam habilitadas.

## Regras de manutenção

1. Edite apenas a versão em `.agents/skills/`.
2. O adaptador Claude só pode apontar para a canônica.
3. Execute `python scripts/validate_studio.py` após alterações.
4. Reinicie o agente se uma skill recém-criada não aparecer no seletor.
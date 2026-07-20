# Quality Standard

## Fonte de verdade

`references/approved_examples/` (o **conjunto inteiro**) é a autoridade visual —
analise todos, não só um. `benchmark_post_01.png` define **atmosfera, cor, fundo
e acabamento**, mas **não** é o template de layout: os carrosséis aprovados
mostram a variedade real (screenshot do produto grande, cards de feature
numerados, tiles de KPI, tabelas/painéis reais). Em conflito com qualquer regra
genérica, os exemplos aprovados vencem — exceto na marca: o nome é sempre
`Asset Lens` e o logo é sempre o oficial, mesmo que exemplos antigos mostrem
"Asset Lens Data".

## Checklist obrigatório (antes de concluir)

Entrega:

- [ ] PNG existente na pasta `instagram/AAAA-MM-DD-<slug>/`;
- [ ] `copy.md` existente na mesma pasta;
- [ ] `verify_output.py` passou (proporção, disclaimer, hashtags, lint).

Arte:

- [ ] formato correto (4:5, 1:1 ou 9:16) e largura 1080;
- [ ] background escuro navy coerente com os approved_examples (nunca mais
      claro que as referências; sem grid quadriculado não solicitado);
- [ ] layout variado e adequado ao tema — **não** um gráfico de linha quando o
      assunto não é série temporal (preferir screenshot/steps/stats/sectors);
- [ ] nome "Asset Lens" correto e logo oficial com transparência;
- [ ] headline legível em tela de celular (testar mentalmente a miniatura);
- [ ] textos dentro das margens seguras, sem cortes;
- [ ] chips curtos, com ícones coerentes com o texto;
- [ ] CTA equilibrado (nem gritante, nem invisível);
- [ ] disclaimer presente e legível;
- [ ] marca d'água "A" sutil (ou desligada quando atrapalha).

Quando houver screenshot:

- [ ] screenshot real utilizado, dados preservados;
- [ ] nenhuma recriação sintética da interface;
- [ ] screenshot nítido (capturado em 2x quando possível) e **protagonista**;
- [ ] **preenche o painel** — grande e legível, sem ficar minúsculo cercado de
      margem borrada; recortado no essencial antes de usar;
- [ ] inset de detalhe (opcional, desligado por padrão) só quando destacar uma
      região com informação real e legível;
- [ ] moldura e integração coerentes com as referências.

## Enquadramento e legibilidade (obrigatório)

Depois de renderizar, olhe a arte pensando na miniatura do feed:

- o elemento principal (screenshot real, cards, tiles, gráfico) **ocupa o
  painel** e é legível — nada essencial some na miniatura;
- o painel **não** é maioria margem/fundo vazio em volta de um elemento pequeno;
- headline e textos não estão cortados nem estourando as margens;
- números/rótulos do produto (em screenshots) dão para ler.

Reprovou em qualquer item → recortar melhor o screenshot ou trocar o visual e
**re-renderizar**.

## Auto-revisão visual (procedimento)

Após renderizar, **ler o PNG** e comparar com o **conjunto** de
`approved_examples/` (não só o benchmark):

1. **Família visual** — a peça parece irmã dos aprovados? (fundo, glows,
   painel glass, contraste, densidade)
2. **Enquadramento e legibilidade** — o elemento principal preenche o painel e
   é legível; nada minúsculo com margem vazia; headline/textos sem corte.
3. **Variedade/adequação** — o visual combina com o tema; não é gráfico de
   linha quando o assunto não é série temporal.
4. **Hierarquia** — eyebrow → headline → subtítulo → chips → visual → CTA →
   disclaimer, sem competição entre elementos.
5. **Tipografia** — headline Poppins bold com linha de acento colorida;
   textos de apoio limpos, sem quebras feias.
6. **Cor** — ciano/teal/azul como destaque; vermelho/amarelo apenas em
   indicadores (drawdown, faixas, tiles de KPI).
7. **Acabamento** — glow sutil (não neon estourado), cantos arredondados
   consistentes, nada com cara de template genérico.

Reprovou → ajustar `render.json` (visual, dados, recorte) e re-renderizar
(máx. 3 iterações).

## Compliance

O lint automático de `verify_output.py` cobre os termos proibidos, o
disclaimer e o limite de 4 hashtags — mas a responsabilidade é editorial
também: a peça inteira deve soar informacional. Nada de promessa de retorno,
call de compra/venda, urgência promocional ou tom de aconselhamento.
Vocabulário preferido: leitura quantitativa, métricas históricas, faixas
quantitativas, risco, ciclos, contexto, acompanhamento, histórico,
informacional.

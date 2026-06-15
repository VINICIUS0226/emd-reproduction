# Resumo do artigo

O artigo investiga o uso de Large Language Models para Equivalent Mutant Detection (EMD), isto e, a classificacao de pares de programas/mutantes como equivalentes ou nao equivalentes. Mutantes equivalentes sao um problema classico em teste de mutacao porque possuem comportamento indistinguivel do programa original para todos os testes possiveis, mas ainda assim aumentam custo e distorcem o mutation score.

## Perguntas de pesquisa

1. LLMs superam tecnicas existentes de EMD?
2. Qual estrategia com LLM funciona melhor?
3. As tecnicas acertam/erram exemplos diferentes, isto e, sao ortogonais?
4. Qual e o custo de treino e inferencia?

## Desenho experimental

Os autores usam 3.302 pares de metodos Java derivados do MutantBench. O pacote contem uma base de codigo com metodos/mutantes e arquivos de pares com os identificadores dos dois codigos e o rotulo binario:

- `1`: par equivalente;
- `0`: par nao equivalente.

As estrategias avaliadas incluem baselines tradicionais, modelos baseados em arvore e diferentes usos de LLMs: embeddings pre-treinados, embeddings fine-tuned, zero-shot prompting, few-shot prompting e fine-tuning por instrucao.

## Resultado principal

O resultado central e que LLMs melhoram substancialmente o desempenho em EMD, especialmente quando usados como modelos de embedding fine-tuned. O melhor resultado reportado no artigo foi obtido com UniXCoder fine-tuned, superando as demais combinacoes de modelos e estrategias.

## Implicacao para esta reproducao

Como alguns modelos exigem GPU grande ou APIs pagas, esta reproducao prioriza:

- pipeline de dados fiel ao pacote dos autores;
- baselines leves executaveis em CPU;
- comparacao documentada com os numeros publicados;
- possibilidade de extensao futura para embeddings e fine-tuning se houver recurso.


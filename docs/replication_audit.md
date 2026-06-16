# Auditoria da Replicacao

Este documento resume os artefatos executados neste repositorio para a replicacao
parcial de Equivalent Mutant Detection (EMD) com baselines leves e comparacao com
resultados oficiais de LLMs.

## Dados

- Fonte: pacote oficial `tianzhaotju/EMD`.
- Treino: `Mutant_A_hierarchical.csv`, com 1652 pares.
- Teste: `Mutant_B_hierarchical.csv`, com 1650 pares.
- Base de codigo: `MutantBench_code_db_java.csv`.
- Dados processados:
  - `data/processed/train.csv`;
  - `data/processed/test.csv`.

## Execucoes Locais

Foram executados localmente em CPU:

- Logistic Regression;
- Linear SVM;
- Random Forest;
- KNN;
- `tce_proxy`;
- checkpoint oficial `Text-Embedding-3-Small`.

O ambiente de execucao esta registrado em:

- `results/environment/environment.json`;
- `results/environment/environment.md`.

## Resultados Locais

| Metodo | Accuracy | Precision | Recall | F1 | Media |
| --- | ---: | ---: | ---: | ---: | --- |
| KNN | 0.9291 | 0.8882 | 0.6064 | 0.7208 | Binaria |
| Random Forest | 0.8964 | 0.6393 | 0.7189 | 0.6767 | Binaria |
| Text-Embedding-3-Small checkpoint | 0.9121 | 1.0000 | 0.4177 | 0.5892 | Binaria |
| Linear SVM | 0.8612 | 0.5336 | 0.6386 | 0.5814 | Binaria |
| Logistic Regression | 0.8436 | 0.4866 | 0.6586 | 0.5597 | Binaria |
| TCE proxy | 0.8491 | 0.0000 | 0.0000 | 0.0000 | Binaria |
| Text-Embedding-3-Small checkpoint | 0.9121 | 0.9531 | 0.7088 | 0.7700 | Macro |

Arquivos consolidados:

- `results/final_summary/model_summary.csv`;
- `results/final_summary/executed_methods_summary.png`;
- `results/final_summary/executed_methods_summary.pdf`.

## Checkpoint Oficial Executado

Foi baixado do Zenodo o pacote:

- `Text_Embedding_small_3.zip`.

Ele foi armazenado em:

- `external/EMD/downloaded_checkpoints/Text_Embedding_small_3.zip`.

Os arquivos extraidos e usados na execucao foram:

- `external/EMD/Text-Embedding-3-Small/saved_models/checkpoints/text-embedding-3-small.bin`;
- `external/EMD/Text-Embedding-3-Small/saved_models/embeddings/text-embedding-3-small.npy`.

Resultados:

- `results/official_text_embedding_small/metrics.json`;
- `results/official_text_embedding_small/predictions.csv`;
- `results/official_text_embedding_small/confusion_matrix.csv`.

## API OpenAI

Foi preparada uma amostra estratificada com 20 pares:

- `results/openai_stratified_sample/sample.csv`.

Tambem foi registrado o template de prompt:

- `results/openai_stratified_sample/prompt_template.txt`.

Na execucao registrada, chamadas de API nao foram feitas porque a variavel
`OPENAI_API_KEY` nao estava configurada. O manifesto da execucao esta em:

- `results/openai_stratified_sample/run_info.json`.

## Comparacoes com Resultados Oficiais

Os resultados oficiais de LLMs foram agregados a partir dos arquivos:

- `external/EMD/results/LLM_strategies_all_operators.csv`;
- `external/EMD/results/EMD_categories_all_operators.csv`.

Esses valores sao usados como referencia externa do artigo original.

Principais saidas:

- `results/figures_llm_comparison/official_llm_strategies_weighted_accuracy.csv`;
- `results/figures_llm_comparison/official_categories_vs_local_baselines_accuracy.csv`;
- `results/figures_llm_comparison/official_llm_top10_operator_heatmap.png`.

## Observacoes Metodologicas

- O `tce_proxy` e deterministico e conservador, mas nao compila os projetos Java.
  Ele marca equivalencia apenas quando os fragmentos normalizados sao identicos.
- O checkpoint `Text-Embedding-3-Small` foi executado localmente com PyTorch CPU.
- Os resultados oficiais por operador somam 1987 ocorrencias ao agregar os
  denominadores, enquanto o split local de teste tem 1650 pares.
- Por essa diferenca, resultados oficiais por operador devem ser interpretados
  como referencia agregada do pacote original, nao como metricas locais sobre o
  mesmo `test.csv`.


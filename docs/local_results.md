# Resultados Locais

Execucoes em CPU usando os splits do pacote dos autores:

- treino: `Mutant_A_hierarchical.csv`, com 1652 pares;
- teste: `Mutant_B_hierarchical.csv`, com 1650 pares.

## Baselines Supervisionados

Configuracao:

- representacao textual do par de metodos Java;
- TF-IDF de n-gramas de caracteres;
- modelos supervisionados leves.

| Modelo | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.8436 | 0.4866 | 0.6586 | 0.5597 |
| Linear SVM | 0.8612 | 0.5336 | 0.6386 | 0.5814 |
| Random Forest | 0.8964 | 0.6393 | 0.7189 | 0.6767 |
| KNN | 0.9291 | 0.8882 | 0.6064 | 0.7208 |

## Baseline Deterministico

| Metodo | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| TCE proxy | 0.8491 | 0.0000 | 0.0000 | 0.0000 |

O `tce_proxy` marcou como equivalente apenas pares com codigo identico apos
normalizacao de comentarios e espacos. Nenhum par equivalente foi identificado
por essa regra no split de teste.

## Checkpoint Oficial Text-Embedding-3-Small

| Metodo | Accuracy | Precision | Recall | F1 | Media |
| --- | ---: | ---: | ---: | ---: | --- |
| Text-Embedding-3-Small checkpoint | 0.9121 | 1.0000 | 0.4177 | 0.5892 | Binaria |
| Text-Embedding-3-Small checkpoint | 0.9121 | 0.9531 | 0.7088 | 0.7700 | Macro |

O resultado macro corresponde ao criterio usado pelo script oficial do pacote
`Text-Embedding-3-Small`.

## Arquivos

- `results/baselines/summary.csv`;
- `results/deterministic/tce_proxy/metrics.json`;
- `results/official_text_embedding_small/metrics.json`;
- `results/final_summary/model_summary.csv`.


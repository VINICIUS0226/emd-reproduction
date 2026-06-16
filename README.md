# Replicacao parcial de LLMs para deteccao de mutantes equivalentes

Este repositorio acompanha o artigo em preparacao:

> Avaliando o Custo e a Eficacia de Large Language Models na Deteccao de Mutantes Equivalentes

O objetivo do artigo e discutir, de forma exploratoria, o uso de tecnicas
tradicionais e abordagens baseadas em Large Language Models (LLMs) para
Equivalent Mutant Detection (EMD). O estudo parte do pacote de replicacao do
artigo:

> Zhao Tian, Honglin Shu, Dong Wang, Xuejie Cao, Yasutaka Kamei, Junjie Chen.
> "Large Language Models for Equivalent Mutant Detection: How Far Are We?"
> ISSTA 2024.

Repositorio original dos autores: <https://github.com/tianzhaotju/EMD>

## Ideia do artigo

Mutantes equivalentes sao variantes de programa que mudam a sintaxe, mas
preservam o comportamento observavel. Eles sao um problema importante em teste
de mutacao porque nao podem ser mortos por testes, aumentam o custo de inspecao
manual e podem distorcer o escore de mutacao.

O artigo que este repositorio apoia pretende avaliar a seguinte tensao:

- LLMs e modelos pre-treinados para codigo tendem a capturar informacao
  semantica mais rica.
- Tecnicas leves, como classificadores tradicionais, sao mais baratas,
  executaveis em CPU e mais simples de reproduzir.
- Em ambientes academicos com restricoes de hardware e custo, nem sempre e
  viavel reexecutar LLMs grandes, fine-tuning completo ou APIs pagas.

Por isso, este repositorio deve ser entendido como uma **replicacao parcial sob
restricoes de recursos**, nao como reproducao integral de todos os experimentos
do artigo original.

## O que foi pretendido

A proposta inicial era comparar:

- baselines tradicionais leves;
- tecnicas deterministicas, como TCE;
- modelos pre-treinados para codigo, como CodeBERT, CodeT5+ e UniXCoder;
- LLMs via prompting ou API;
- estrategias hibridas em que modelos leves filtram casos simples e LLMs ficam
  reservados para casos ambiguos.

Durante a execucao, a parte viavel localmente foi concentrada em:

- preparar os dados do MutantBench fornecidos pelos autores;
- treinar baselines leves em CPU;
- gerar metricas e figuras locais;
- comparar os resultados locais com os resultados oficiais agregados dos LLMs
  publicados no pacote original.

## O que foi executado de fato

Foram reexecutados localmente:

- processamento dos dados;
- treinamento em CPU dos modelos:
  - Logistic Regression;
  - Linear SVM;
  - Random Forest;
  - KNN;
- avaliacao no split de teste;
- geracao de:
  - `accuracy`;
  - `precision`;
  - `recall`;
  - `F1`;
  - matriz de confusao;
  - predicoes por exemplo;
  - figuras em PNG/PDF.

Nao foram reexecutados localmente:

- GPT-3.5/GPT-4 via API;
- embeddings pagos da OpenAI;
- Code Llama 7B;
- StarCoder 7B;
- CodeT5+ 6B;
- fine-tuning completo de CodeBERT, CodeT5, UniXCoder ou modelos maiores;
- TCE.

Os resultados de LLMs usados nas figuras comparativas foram extraidos dos CSVs
oficiais do pacote dos autores, e nao de uma nova inferencia local.

## Estrutura do repositorio

```text
.
|-- README.md
|-- requirements.txt
|-- configs/
|   `-- baseline.yaml
|-- data/
|   `-- processed/
|       |-- train.csv
|       `-- test.csv
|-- docs/
|   |-- paper_summary.md
|   |-- reproduction_plan.md
|   |-- limitations.md
|   |-- local_results.md
|   `-- replication_audit.md
|-- external/
|   `-- EMD/
|       |-- dataset/
|       |-- results/
|       |-- figs/
|       `-- <scripts do pacote original>
|-- results/
|   |-- baselines/
|   |-- figures/
|   `-- figures_llm_comparison/
|-- scripts/
|   |-- download_author_repo.ps1
|   |-- prepare_dataset.py
|   `-- generate_llm_comparison_figures.py
`-- src/
    `-- emd_repro/
        |-- data.py
        |-- features.py
        |-- metrics.py
        `-- train_baselines.py
```

## Ambiente

A execucao local foi feita em Python com bibliotecas leves de ciencia de dados e
aprendizado de maquina:

- `pandas`;
- `numpy`;
- `scikit-learn`;
- `PyYAML`;
- `joblib`;
- `matplotlib`;
- `seaborn`.

O arquivo de dependencias esta em:

```text
requirements.txt
```

Os LLMs nao foram reexecutados porque o ambiente local nao continha:

- `torch`;
- `transformers`;
- `openai`;
- variavel `OPENAI_API_KEY`;
- checkpoints oficiais dos modelos fine-tuned.

## Passo a passo para reproduzir

### 1. Criar e ativar o ambiente

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Obter o pacote dos autores

O pacote original ja esta versionado em `external/EMD`. Caso precise baixar de
novo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/download_author_repo.ps1
```

### 3. Preparar os dados

```powershell
python scripts/prepare_dataset.py --author-repo external/EMD --out data/processed
```

O script usa:

- `external/EMD/dataset/Mutant_A_hierarchical.csv` como treino;
- `external/EMD/dataset/Mutant_B_hierarchical.csv` como teste;
- `external/EMD/dataset/MutantBench_code_db_java.csv` como base de codigo.

Saidas:

```text
data/processed/train.csv
data/processed/test.csv
```

### 4. Rodar os baselines leves

```powershell
python -m src.emd_repro.train_baselines --data data/processed --out results/baselines
```

Modelos treinados:

- Logistic Regression;
- Linear SVM;
- Random Forest;
- KNN.

Saidas principais:

```text
results/baselines/summary.csv
results/baselines/<modelo>/metrics.json
results/baselines/<modelo>/confusion_matrix.csv
results/baselines/<modelo>/predictions.csv
results/baselines/<modelo>/model.joblib
```

### 5. Gerar figuras dos baselines locais

As figuras locais ja estao em `results/figures`. Elas foram geradas a partir dos
arquivos em `results/baselines`.

Principais arquivos:

```text
results/figures/baseline_metrics_comparison.png
results/figures/baseline_f1_ranking.png
results/figures/baseline_confusion_matrices.png
results/figures/dataset_class_distribution.png
results/figures/baseline_summary_table.png
```

Tambem ha versoes `.pdf` para uso em artigo.

### 6. Gerar comparacoes com resultados oficiais de LLMs

```powershell
python scripts/generate_llm_comparison_figures.py
```

Esse script usa:

```text
external/EMD/results/LLM_strategies_all_operators.csv
external/EMD/results/EMD_categories_all_operators.csv
results/baselines/summary.csv
```

Saidas:

```text
results/figures_llm_comparison/official_llm_strategies_weighted_accuracy.png
results/figures_llm_comparison/official_categories_vs_local_baselines_accuracy.png
results/figures_llm_comparison/official_llm_top10_operator_heatmap.png
```

Tambem sao gerados arquivos `.csv`, `.pdf` e `comparison_notes.txt`.

## Resultados locais

Execucao em CPU usando os splits do pacote dos autores:

- treino: 1652 pares;
- teste: 1650 pares;
- representacao: concatenacao dos dois metodos Java do par;
- features: TF-IDF de n-gramas de caracteres;
- modelos: Logistic Regression, Linear SVM, Random Forest e KNN.

| Modelo | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.8436 | 0.4866 | 0.6586 | 0.5597 |
| Linear SVM | 0.8612 | 0.5336 | 0.6386 | 0.5814 |
| Random Forest | 0.8964 | 0.6393 | 0.7189 | 0.6767 |
| KNN | 0.9291 | 0.8882 | 0.6064 | 0.7208 |

O melhor baseline local por F1 foi o KNN, com:

- `accuracy = 0.9291`;
- `precision = 0.8882`;
- `recall = 0.6064`;
- `F1 = 0.7208`.

## Comparacao com resultados oficiais de LLMs

Os resultados abaixo foram agregados a partir dos CSVs oficiais do pacote dos
autores. Eles devem ser citados como **resultados oficiais do artigo original**,
nao como resultados reexecutados localmente.

| Estrategia LLM oficial | Accuracy ponderada |
| --- | ---: |
| Fine-tuned Code Embedding | 0.9331 |
| Pre-trained Code Embedding | 0.9215 |
| Fine-tuning with Instruction | 0.9205 |
| Few-shot Prompting | 0.8525 |
| Zero-shot Prompting | 0.7856 |

Comparacao geral entre categorias oficiais e baselines locais:

| Metodo/Categoria | Accuracy |
| --- | ---: |
| LLM-based | 0.9331 |
| Local KNN | 0.9291 |
| Local Random Forest | 0.8964 |
| ML-based | 0.8782 |
| Local Linear SVM | 0.8612 |
| Local Logistic Regression | 0.8436 |
| Tree-based NN | 0.8279 |
| Compiler-based | 0.6714 |

Interpretacao: o melhor baseline local ficou proximo da categoria LLM-based
oficial. Contudo, essa comparacao deve ser lida com cautela, pois os LLMs nao
foram reexecutados no mesmo ambiente local.

## Figuras para usar no artigo

Figuras dos experimentos locais:

```text
results/figures/baseline_metrics_comparison.png
results/figures/baseline_f1_ranking.png
results/figures/baseline_confusion_matrices.png
results/figures/dataset_class_distribution.png
results/figures/baseline_summary_table.png
```

Figuras de comparacao com resultados oficiais de LLMs:

```text
results/figures_llm_comparison/official_llm_strategies_weighted_accuracy.png
results/figures_llm_comparison/official_categories_vs_local_baselines_accuracy.png
results/figures_llm_comparison/official_llm_top10_operator_heatmap.png
```

As versoes `.pdf` correspondentes tambem estao nas mesmas pastas.

## Como relatar no artigo

Formulacao recomendada:

> Realizamos uma replicacao parcial sob restricoes de hardware e custo. O
> pipeline de dados e os baselines leves foram reexecutados localmente em CPU.
> Para os LLMs, como os checkpoints fine-tuned e as APIs pagas nao estavam
> disponiveis, comparamos os resultados locais com os resultados oficiais
> agregados fornecidos no pacote de replicacao dos autores. Portanto, os
> resultados de LLMs devem ser interpretados como referencia externa do estudo
> original, e nao como inferencia reexecutada nesta infraestrutura.

Evite afirmar que todos os LLMs foram reproduzidos. O mais correto e descrever o
trabalho como:

- replicacao parcial;
- estudo exploratorio;
- comparacao entre baselines locais e resultados oficiais agregados;
- analise de viabilidade sob restricoes de custo e hardware.

## Limitacoes

- Os LLMs nao foram reexecutados localmente.
- Os checkpoints oficiais fine-tuned nao estavam disponiveis no ambiente.
- Nao havia chave de API para modelos proprietarios.
- TCE foi discutido no artigo, mas nao implementado nesta execucao.
- O split local de teste tem 1650 pares, enquanto os CSVs oficiais por operador
  somam 1987 ocorrencias ao agregar os denominadores. Por isso, os resultados
  oficiais por operador nao devem ser tratados como avaliacao local exatamente
  sobre o mesmo `test.csv`.
- A copia local de `MutantBench_code_db_java.csv` contem apenas `id` e `code`;
  sem a coluna de operador, nao foi possivel calcular resultados locais por
  operador de mutacao.

## Proximos passos para fortalecer o artigo

1. Executar pelo menos um modelo de embedding local pequeno, como CodeBERT ou
   UniXCoder, se houver instalacao de `torch` e `transformers`.
2. Rodar uma amostra estratificada com API, registrando prompt, modelo, data,
   temperatura, custo e tempo.
3. Baixar checkpoints oficiais do Zenodo para testar os modelos fine-tuned dos
   autores.
4. Implementar ou integrar TCE como baseline deterministico.
5. Registrar hardware, sistema operacional, versoes das dependencias e tempo de
   execucao.
6. Atualizar o texto do artigo para substituir promessas de avaliacao futura por
   resultados efetivamente executados.

## Documentos auxiliares

- `docs/paper_summary.md`: resumo do artigo original.
- `docs/reproduction_plan.md`: plano de reproducao.
- `docs/local_results.md`: resultados locais dos baselines.
- `docs/limitations.md`: limitacoes gerais.
- `docs/replication_audit.md`: auditoria metodologica da replicacao.

## Observacao sobre versionamento

Este repositorio inclui os dados processados, resultados, figuras e o pacote
externo `external/EMD` como artefatos de reproducao. O ambiente virtual
`.venv/`, caches Python e arquivos `.DS_Store` permanecem ignorados.


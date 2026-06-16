# Replicacao Parcial de EMD com Baselines e LLMs

Este repositorio contem os artefatos de uma replicacao parcial do estudo:

> Zhao Tian, Honglin Shu, Dong Wang, Xuejie Cao, Yasutaka Kamei, Junjie Chen.
> "Large Language Models for Equivalent Mutant Detection: How Far Are We?"
> ISSTA 2024.

O repositorio apoia o artigo "Avaliando o Custo e a Eficacia de Large Language
Models na Deteccao de Mutantes Equivalentes". O foco e avaliar a deteccao de
mutantes equivalentes em pares de metodos Java, combinando execucoes locais em
CPU com comparacoes baseadas nos artefatos oficiais do pacote original.

Repositorio original dos autores: <https://github.com/tianzhaotju/EMD>

## Escopo

Foram executados localmente:

- preparacao dos dados do MutantBench;
- baselines supervisionados leves com TF-IDF de n-gramas de caracteres;
- baseline deterministico conservador (`tce_proxy`);
- inferencia em CPU do checkpoint oficial `Text-Embedding-3-Small`;
- geracao de metricas, predicoes, matrizes de confusao e figuras.

Tambem foram geradas comparacoes com resultados oficiais de LLMs presentes no
pacote dos autores. Esses resultados oficiais sao usados como referencia externa,
nao como nova inferencia local.

## Estrutura

```text
.
|-- configs/
|   `-- baseline.yaml
|-- data/
|   `-- processed/
|       |-- train.csv
|       `-- test.csv
|-- docs/
|   |-- limitations.md
|   |-- local_results.md
|   |-- paper_summary.md
|   |-- replication_audit.md
|   `-- reproduction_plan.md
|-- external/
|   `-- EMD/
|       |-- dataset/
|       |-- downloaded_checkpoints/
|       |-- results/
|       `-- Text-Embedding-3-Small/
|-- results/
|   |-- baselines/
|   |-- deterministic/
|   |-- environment/
|   |-- figures/
|   |-- figures_llm_comparison/
|   |-- final_summary/
|   |-- official_text_embedding_small/
|   `-- openai_stratified_sample/
|-- scripts/
|   |-- download_author_repo.ps1
|   |-- generate_final_summary.py
|   |-- generate_llm_comparison_figures.py
|   |-- prepare_dataset.py
|   |-- record_environment.py
|   |-- run_official_text_embedding_small.py
|   `-- run_openai_stratified_sample.py
`-- src/
    `-- emd_repro/
        |-- data.py
        |-- deterministic_baselines.py
        |-- features.py
        |-- metrics.py
        `-- train_baselines.py
```

## Ambiente

O ambiente registrado esta em:

```text
results/environment/environment.json
results/environment/environment.md
```

Resumo:

- Sistema: Windows 10;
- Python: 3.10.5;
- CPU logicas: 12;
- PyTorch: 2.12.0 CPU;
- Transformers: 5.12.1;
- OpenAI SDK: 2.41.1;
- `OPENAI_API_KEY`: nao configurada na execucao registrada.

## Instalacao

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Execucao Passo a Passo

### 1. Preparar dados

```powershell
python scripts/prepare_dataset.py --author-repo external/EMD --out data/processed
```

Entradas:

- `external/EMD/dataset/MutantBench_code_db_java.csv`;
- `external/EMD/dataset/Mutant_A_hierarchical.csv`;
- `external/EMD/dataset/Mutant_B_hierarchical.csv`.

Saidas:

- `data/processed/train.csv`;
- `data/processed/test.csv`.

### 2. Rodar baselines supervisionados

```powershell
python -m src.emd_repro.train_baselines --data data/processed --out results/baselines
```

Modelos:

- Logistic Regression;
- Linear SVM;
- Random Forest;
- KNN.

### 3. Rodar baseline deterministico

```powershell
python -m src.emd_repro.deterministic_baselines --data data/processed --out results/deterministic
```

O `tce_proxy` classifica como equivalente apenas pares cujo codigo normalizado
fica identico apos remocao de comentarios e espacos. Ele e um baseline
deterministico conservador, nao uma implementacao completa de TCE por compilacao.

### 4. Rodar checkpoint oficial Text-Embedding-3-Small

O menor checkpoint oficial foi baixado do Zenodo para:

```text
external/EMD/downloaded_checkpoints/Text_Embedding_small_3.zip
```

O ZIP contem:

- `text-embedding-3-small.bin`;
- `text-embedding-3-small.npy`.

Execucao:

```powershell
python scripts/run_official_text_embedding_small.py
```

Saidas:

- `results/official_text_embedding_small/metrics.json`;
- `results/official_text_embedding_small/predictions.csv`;
- `results/official_text_embedding_small/confusion_matrix.csv`.

### 5. Preparar amostra estratificada para API OpenAI

```powershell
python scripts/run_openai_stratified_sample.py --sample-size 20 --model gpt-5.5 --temperature 0
```

Na execucao registrada, a chave `OPENAI_API_KEY` nao estava configurada. Por
isso, o script salvou a amostra e o template de prompt, mas nao realizou chamadas
de API.

Saidas:

- `results/openai_stratified_sample/sample.csv`;
- `results/openai_stratified_sample/prompt_template.txt`;
- `results/openai_stratified_sample/run_info.json`.

Para executar as chamadas de API, configure a chave antes do comando:

```powershell
$env:OPENAI_API_KEY="sua-chave"
python scripts/run_openai_stratified_sample.py --sample-size 20 --model gpt-5.5 --temperature 0
```

### 6. Registrar ambiente

```powershell
python scripts/record_environment.py
```

### 7. Gerar figuras e resumo final

```powershell
python scripts/generate_llm_comparison_figures.py
python scripts/generate_final_summary.py
```

## Resultados Executados Localmente

Resultados principais com media binaria para a classe equivalente:

| Metodo | Origem | Accuracy | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| KNN | Local CPU | 0.9291 | 0.8882 | 0.6064 | 0.7208 |
| Random Forest | Local CPU | 0.8964 | 0.6393 | 0.7189 | 0.6767 |
| Text-Embedding-3-Small checkpoint | Checkpoint oficial em CPU | 0.9121 | 1.0000 | 0.4177 | 0.5892 |
| Linear SVM | Local CPU | 0.8612 | 0.5336 | 0.6386 | 0.5814 |
| Logistic Regression | Local CPU | 0.8436 | 0.4866 | 0.6586 | 0.5597 |
| TCE proxy | Local CPU | 0.8491 | 0.0000 | 0.0000 | 0.0000 |

O checkpoint `Text-Embedding-3-Small` tambem reproduziu as metricas macro do
script oficial:

| Metodo | Accuracy | Precision macro | Recall macro | F1 macro |
| --- | ---: | ---: | ---: | ---: |
| Text-Embedding-3-Small checkpoint | 0.9121 | 0.9531 | 0.7088 | 0.7700 |

Resumo consolidado:

```text
results/final_summary/model_summary.csv
results/final_summary/executed_methods_summary.png
results/final_summary/executed_methods_summary.pdf
```

## Comparacao com Resultados Oficiais

Resultados oficiais agregados por estrategia LLM, extraidos de
`external/EMD/results/LLM_strategies_all_operators.csv`:

| Estrategia oficial | Accuracy ponderada |
| --- | ---: |
| Fine-tuned Code Embedding | 0.9331 |
| Pre-trained Code Embedding | 0.9215 |
| Fine-tuning with Instruction | 0.9205 |
| Few-shot Prompting | 0.8525 |
| Zero-shot Prompting | 0.7856 |

Comparacao entre categorias oficiais e baselines locais:

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

Figuras:

```text
results/figures_llm_comparison/official_llm_strategies_weighted_accuracy.png
results/figures_llm_comparison/official_categories_vs_local_baselines_accuracy.png
results/figures_llm_comparison/official_llm_top10_operator_heatmap.png
```

## Figuras

Figuras locais:

```text
results/figures/baseline_metrics_comparison.png
results/figures/baseline_f1_ranking.png
results/figures/baseline_confusion_matrices.png
results/figures/dataset_class_distribution.png
results/figures/baseline_summary_table.png
```

Figura consolidada:

```text
results/final_summary/executed_methods_summary.png
```

As pastas de figuras tambem contem versoes `.pdf`.

## Observacoes Metodologicas

- Os baselines supervisionados e o `tce_proxy` foram executados localmente em CPU.
- O checkpoint `Text-Embedding-3-Small` foi baixado do Zenodo e executado
  localmente em CPU.
- Os resultados oficiais de LLMs foram agregados a partir dos CSVs publicados no
  pacote original.
- A amostra para API OpenAI foi preparada, mas chamadas de API nao foram feitas
  porque `OPENAI_API_KEY` nao estava configurada.
- O split local de teste contem 1650 pares. Os CSVs oficiais por operador somam
  1987 ocorrencias ao agregar denominadores por operador; portanto, as
  comparacoes por operador devem ser interpretadas como referencia oficial
  agregada.

## Artefatos Versionados

O repositorio inclui:

- dados processados;
- pacote original em `external/EMD`;
- checkpoint oficial menor baixado do Zenodo;
- predicoes e metricas;
- figuras PNG/PDF;
- scripts de reproducao.

Nao sao versionados:

- ambiente virtual `.venv/`;
- caches Python;
- arquivos `.DS_Store`.


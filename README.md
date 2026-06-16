# Reproducao parcial: Large Language Models for Equivalent Mutant Detection

Este repositorio organiza uma reproducao de baixo custo do artigo:

> Zhao Tian, Honglin Shu, Dong Wang, Xuejie Cao, Yasutaka Kamei, Junjie Chen.
> "Large Language Models for Equivalent Mutant Detection: How Far Are We?" ISSTA 2024.

Repositorio original dos autores: https://github.com/tianzhaotju/EMD

## Objetivo

Reproduzir, dentro de restricoes de hardware e custo, parte dos estudos sobre Equivalent Mutant Detection (EMD) em pares de metodos Java:

- preparacao dos dados do pacote original;
- avaliacao de baselines leves de machine learning;
- avaliacao opcional de embeddings de codigo/texto;
- geracao de metricas comparaveis: precision, recall, F1, accuracy e matriz de confusao;
- documentacao explicita do que nao foi reproduzido por exigir GPU grande ou APIs pagas.

## Escopo da reproducao

| Parte do artigo | Status neste repositorio | Motivo |
| --- | --- | --- |
| Dataset MutantBench pre-processado | Reproduzivel | Disponivel no pacote dos autores |
| Baselines ML leves | Reproduzivel | Executavel em CPU |
| Embeddings locais pequenos | Opcional | Depende de download de modelo |
| UniXCoder/CodeBERT fine-tuning completo | Planejado/opcional | Pode exigir GPU e tempo |
| CodeT5+, StarCoder, Code Llama 7B | Nao reproduzido por padrao | Exige GPU grande |
| GPT-3.5/GPT-4/Text-Embedding API | Nao reproduzido por padrao | Exige custo com API |

## Estrutura

```text
.
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- docs/
|   |-- paper_summary.md
|   |-- reproduction_plan.md
|   `-- limitations.md
|-- scripts/
|   |-- download_author_repo.ps1
|   `-- prepare_dataset.py
|-- src/
|   `-- emd_repro/
|       |-- __init__.py
|       |-- data.py
|       |-- features.py
|       |-- metrics.py
|       `-- train_baselines.py
|-- configs/
|   `-- baseline.yaml
`-- results/
    `-- .gitkeep
```

## Como executar

1. Criar ambiente:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Baixar o pacote dos autores:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/download_author_repo.ps1
```

3. Preparar dados:

```bash
python scripts/prepare_dataset.py --author-repo external/EMD --out data/processed
```

4. Rodar baselines leves:

```bash
python -m src.emd_repro.train_baselines --data data/processed --out results/baselines
```

5. Gerar figuras de comparacao com os resultados oficiais de LLMs do pacote original:

```bash
python scripts/generate_llm_comparison_figures.py
```

As figuras locais ficam em `results/figures` e as comparacoes com resultados
oficiais de LLMs ficam em `results/figures_llm_comparison`.

## Como interpretar

O artigo reporta que estrategias baseadas em LLM superam baselines tradicionais, e que a melhor combinacao foi UniXCoder com embeddings fine-tuned. Este repositorio nao tenta mascarar limitacoes de recurso: os resultados produzidos aqui devem ser apresentados como reproducao parcial e estudo de viabilidade.

Para TCC, artigo de disciplina ou relatorio, use:

- `docs/paper_summary.md` para explicar o artigo;
- `docs/reproduction_plan.md` para justificar o protocolo;
- `docs/limitations.md` para declarar modelos nao executados e motivos.
- `docs/local_results.md` para relatar a execucao local dos baselines leves.
- `docs/replication_audit.md` para separar o que foi reexecutado localmente do
  que foi apenas comparado com artefatos oficiais dos autores.



Nota sobre os dados: no pacote atual dos autores, os splits sao `Mutant_A_hierarchical.csv` e `Mutant_B_hierarchical.csv`. O script usa A como treino e B como teste.

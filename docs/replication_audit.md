# Auditoria da replicacao

Esta auditoria resume o estado atual da replicacao local do artigo
"Large Language Models for Equivalent Mutant Detection: How Far Are We?".

## O que foi reproduzido localmente

- Preparacao dos dados a partir do pacote dos autores.
- Uso dos splits `Mutant_A_hierarchical.csv` como treino e `Mutant_B_hierarchical.csv` como teste.
- Treinamento e avaliacao em CPU dos baselines leves:
  - Logistic Regression;
  - Linear SVM;
  - Random Forest;
  - KNN.
- Geracao de metricas locais:
  - accuracy;
  - precision;
  - recall;
  - F1;
  - matriz de confusao;
  - predicoes por exemplo.
- Geracao de figuras em PNG/PDF para uso no artigo em `results/figures`.

## O que foi comparado, mas nao reexecutado

Os resultados de LLMs foram comparados a partir dos CSVs oficiais presentes no
pacote de replicacao dos autores:

- `external/EMD/results/LLM_strategies_all_operators.csv`;
- `external/EMD/results/EMD_categories_all_operators.csv`.

As figuras correspondentes foram geradas em `results/figures_llm_comparison`.
Esses graficos devem ser descritos como comparacao com resultados oficiais do
pacote original, nao como inferencia LLM reexecutada neste ambiente.

## Por que os LLMs nao foram reexecutados

No ambiente local auditado nao estavam disponiveis:

- `torch`;
- `transformers`;
- `openai`;
- variavel `OPENAI_API_KEY`;
- checkpoints `.bin`, `.pt`, `.pth`, `.npy`, `.safetensors` ou `.ckpt` dos modelos.

O README do pacote original tambem recomenda GPU com pelo menos 48 GB de memoria
para os LLMs open-source maiores. Modelos fechados, como GPT-3.5/GPT-4 e
embeddings da OpenAI, exigem chave de API e custo de uso.

## Divergencia importante encontrada

O split local de teste tem 1650 pares. Entretanto, os CSVs oficiais por operador
somam 1987 ocorrencias ao agregar os denominadores reportados em cada operador.
Por isso, os graficos oficiais por operador nao devem ser tratados como uma
avaliacao local sobre exatamente o mesmo `test.csv` processado neste repositorio.

Essa diferenca deve ser explicada no artigo como uma limitacao da comparacao:
os baselines locais foram reexecutados no split local, enquanto os resultados por
operador de LLMs foram extraidos dos artefatos oficiais agregados do artigo.

## Lacunas restantes para uma replicacao mais forte

1. Reexecutar pelo menos um LLM pequeno ou embedding local.
   - Exemplo viavel: CodeBERT/UniXCoder em modo de embedding, se houver GPU ou tempo
     aceitavel em CPU.
   - Exige instalar `torch` e `transformers`, alem de baixar o modelo/checkpoint.

2. Reexecutar GPT/embeddings da OpenAI por amostragem.
   - Exige `OPENAI_API_KEY` e custo de API.
   - Recomendado usar uma amostra estratificada e registrar prompt, modelo, data e custo.

3. Obter checkpoints oficiais do Zenodo.
   - Necessario para testar os modelos fine-tuned dos autores.
   - Sem checkpoints, os scripts `test.py` dos modelos LLM nao reproduzem os resultados
     fine-tuned.

4. Preservar metadados de operador no dataset processado.
   - A copia local de `MutantBench_code_db_java.csv` contem apenas `id` e `code`.
   - Sem operador, nao e possivel calcular resultados locais por operador de mutacao.

5. Registrar ambiente de execucao.
   - Versao do Python;
   - versoes de dependencias;
   - sistema operacional;
   - CPU/GPU;
   - tempo aproximado de execucao.

6. Adicionar uma secao de ameacas a validade.
   - Comparacao parcial;
   - ausencia de fine-tuning LLM;
   - diferenca entre resultados locais e agregados oficiais;
   - dependencia de artefatos publicados pelos autores.

## Formulacao recomendada para o artigo

> Realizamos uma replicacao parcial sob restricoes de hardware e custo. O pipeline
> de dados e os baselines leves foram reexecutados localmente em CPU. Para os
> LLMs, como os checkpoints fine-tuned e as APIs pagas nao estavam disponiveis,
> comparamos os resultados locais com os resultados oficiais agregados fornecidos
> no pacote de replicacao dos autores. Portanto, os resultados de LLMs devem ser
> interpretados como referencia externa do estudo original, e nao como inferencia
> reexecutada nesta infraestrutura.


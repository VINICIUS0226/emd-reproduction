# Plano de reproducao

## Fase 1: infraestrutura

- Criar repositorio de reproducao.
- Referenciar o pacote original dos autores.
- Definir ambiente Python.
- Preparar scripts de download, preprocessamento e avaliacao.

## Fase 2: dados

- Baixar o repositorio `tianzhaotju/EMD`.
- Ler `MutantBench_code_db_java.csv`.
- Ler os arquivos de treino e teste.
- Resolver `code_id_1` e `code_id_2` para os respectivos metodos Java.
- Gerar `train.csv` e `test.csv` normalizados.

## Fase 3: baselines executaveis

- Criar representacao textual do par de codigo.
- Extrair TF-IDF em n-gramas de caracteres.
- Treinar classificadores leves:
  - Logistic Regression;
  - Linear SVM;
  - Random Forest;
  - KNN.

## Fase 4: avaliacao

- Calcular accuracy, precision, recall e F1.
- Salvar predicoes por exemplo.
- Salvar matriz de confusao.
- Comparar qualitativamente com os resultados reportados no artigo.

## Fase 5: extensoes opcionais

- Adicionar SentenceTransformers local.
- Adicionar CodeBERT/UniXCoder somente para inferencia de embeddings.
- Rodar fine-tuning pequeno se houver GPU.


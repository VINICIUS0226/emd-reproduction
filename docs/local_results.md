# Resultados locais

Execucao em CPU usando os splits do pacote dos autores:

- treino: `Mutant_A_hierarchical.csv`;
- teste: `Mutant_B_hierarchical.csv`;
- features: TF-IDF de n-gramas de caracteres;
- modelos: Logistic Regression, Linear SVM, Random Forest e KNN.

| Modelo | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.8436 | 0.4866 | 0.6586 | 0.5597 |
| Linear SVM | 0.8612 | 0.5336 | 0.6386 | 0.5814 |
| Random Forest | 0.8964 | 0.6393 | 0.7189 | 0.6767 |
| KNN | 0.9291 | 0.8882 | 0.6064 | 0.7208 |

Estes resultados nao substituem os resultados dos modelos LLM do artigo. Eles servem como reproducao parcial executavel em CPU e como base para comparacao com estrategias mais caras.


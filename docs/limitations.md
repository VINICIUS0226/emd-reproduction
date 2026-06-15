# Limitacoes da reproducao

Esta reproducao foi planejada para um ambiente sem orcamento para APIs pagas e sem GPU de alto desempenho. Portanto, ela nao executa por padrao:

- GPT-3.5/GPT-4 via API;
- modelos de embedding pagos da OpenAI;
- Code Llama 7B;
- StarCoder 7B;
- CodeT5+ 6B;
- fine-tuning completo dos modelos maiores.

Segundo o pacote dos autores, a execucao de alguns LLMs open-source foi recomendada em GPU com 48 GB ou mais de memoria. Por isso, reproduzir todos os experimentos integralmente nao e realista neste ambiente.

## Como relatar isso academicamente

Use a expressao "reproducao parcial" ou "replicacao parcial sob restricoes de recursos". Evite afirmar que o artigo inteiro foi reproduzido.

Uma formulacao adequada:

> Reproduzimos o fluxo de dados e baselines leves do estudo, mantendo a comparabilidade das metricas. Os experimentos com LLMs de grande porte e APIs pagas foram documentados, mas nao executados por restricoes de hardware e custo.


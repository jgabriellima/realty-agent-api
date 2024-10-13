# Guia de Qualidade de Código

Este documento detalha as práticas, ferramentas e padrões de qualidade de código adotados neste projeto. Seguir essas diretrizes é essencial para manter a consistência, legibilidade e manutenibilidade do nosso código-base.

## Índice

1. [Ferramentas de Qualidade](#ferramentas-de-qualidade)
2. [Padrões de Codificação](#padrões-de-codificação)
3. [Testes e Cobertura](#testes-e-cobertura)
4. [Revisão de Código](#revisão-de-código)
5. [Integração Contínua](#integração-contínua)

## Ferramentas de Qualidade

### Black

Black é nosso formatador de código Python.

- **Configuração**: Definida em `pyproject.toml`
- **Uso**: Executado automaticamente via pre-commit
- **Comando manual**: `poetry run black .`

### isort

isort organiza nossas importações.

- **Configuração**: Definida em `pyproject.toml`, compatível com Black
- **Uso**: Executado automaticamente via pre-commit
- **Comando manual**: `poetry run isort .`

### Flake8

Flake8 verifica o estilo e qualidade do código.

- **Configuração**: Definida em `.flake8`
- **Uso**: Executado automaticamente via pre-commit
- **Comando manual**: `poetry run flake8`

### autopep8

autopep8 corrige automaticamente problemas de estilo.

- **Uso**: Não incluído no pre-commit devido ao tempo de execução
- **Comando manual**: `poetry run autopep8 --in-place --aggressive --aggressive -r .`

## Padrões de Codificação

1. **PEP 8**: Seguimos as diretrizes do PEP 8 para estilo de código Python.
2. **Docstrings**: Use docstrings para todas as funções, classes e módulos.
3. **Tipagem**: Utilize type hints para melhorar a legibilidade e manutenção do código.
4. **Nomes significativos**: Escolha nomes descritivos para variáveis, funções e classes.
5. **DRY (Don't Repeat Yourself)**: Evite duplicação de código.
6. **SOLID**: Aplique os princípios SOLID quando apropriado.

## Testes e Cobertura

### Escrevendo Testes

- Use pytest para escrever e executar testes.
- Escreva testes para todas as novas funcionalidades e correções de bugs.
- Mantenha os testes focados e independentes.

### Executando Testes

- Execute testes localmente antes de push: `poetry run pytest`
- Para testes com cobertura: `poetry run pytest --cov=api_template --cov-report=html`

### Cobertura de Código

- Meta de cobertura: Mínimo de 80% para código novo.
- Revise relatórios de cobertura regularmente.
- Priorize a qualidade dos testes sobre a quantidade.

## Revisão de Código

1. Todos os pull requests devem passar por revisão de código.
2. Verifique se o código segue os padrões e práticas do projeto.
3. Execute todos os testes e verifique a cobertura antes de aprovar.
4. Forneça feedback construtivo e específico.

## Integração Contínua

Nossa pipeline de CI inclui:

1. Execução de todas as ferramentas de qualidade de código.
2. Execução de todos os testes.
3. Geração de relatórios de cobertura.
4. Verificação de dependências e licenças.

Mantenha-se atento às notificações de CI e corrija quaisquer problemas prontamente.

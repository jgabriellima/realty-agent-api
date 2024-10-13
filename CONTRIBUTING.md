# Guia de Contribuição

Agradecemos seu interesse em contribuir para o nosso projeto! Este documento fornece diretrizes para garantir um processo de contribuição suave e eficiente.

## Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Contribuir](#como-contribuir)
3. [Reportando Bugs](#reportando-bugs)
4. [Sugerindo Melhorias](#sugerindo-melhorias)
5. [Processo de Pull Request](#processo-de-pull-request)
6. [Padrões de Codificação](#padrões-de-codificação)
7. [Testes](#testes)

## Código de Conduta

Este projeto e todos os participantes estão sob o [Código de Conduta do Contribuidor](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). Ao contribuir, você concorda em respeitar este código.

## Como Contribuir

1. Fork o repositório e crie seu branch a partir do `main`.
2. Se você adicionou código que deve ser testado, adicione testes.
3. Se você alterou APIs, atualize a documentação.
4. Garanta que o suite de testes passe.
5. Certifique-se de que seu código siga os padrões de estilo do projeto.
6. Faça commit de suas alterações e crie um pull request.

## Reportando Bugs

Bugs são rastreados como issues no GitHub. Ao criar um issue para um bug, inclua:

- Um título claro e descritivo.
- Uma descrição detalhada do problema, incluindo passos para reproduzir.
- As versões relevantes do projeto e do ambiente (SO, Python, etc.).
- Se possível, um código mínimo que reproduza o problema.

## Sugerindo Melhorias

Sugestões de melhorias também são bem-vindas. Ao sugerir uma melhoria, inclua:

- Uma descrição clara e detalhada da melhoria proposta.
- Explicação de por que essa melhoria seria útil para o projeto.
- Se possível, exemplos de como a melhoria funcionaria.

## Processo de Pull Request

1. Certifique-se de que quaisquer dependências de instalação ou compilação sejam removidas antes do final da camada.
2. Atualize o README.md com detalhes das mudanças, incluindo novas variáveis de ambiente, portas expostas, locais de arquivos úteis e parâmetros de contêiner.
3. Aumente os números de versão em quaisquer arquivos de exemplo e no README.md para a nova versão que este Pull Request representaria.
4. Você pode mesclar o Pull Request uma vez que tenha a aprovação de dois outros desenvolvedores, ou se você não tiver permissão para fazer isso, pode solicitar ao segundo revisor que o faça por você.

## Padrões de Codificação

- Siga as diretrizes de estilo definidas no [CODE_QUALITY.md](CODE_QUALITY.md).
- Use type hints para melhorar a legibilidade e manutenção do código.
- Escreva docstrings para todas as funções, classes e módulos.
- Mantenha o código DRY (Don't Repeat Yourself).
- Nomeie variáveis, funções e classes de forma clara e descritiva.

## Testes

- Escreva testes para todas as novas funcionalidades e correções de bugs.
- Mantenha a cobertura de código acima de 80% para código novo.
- Execute `poetry run pytest` para rodar os testes antes de submeter um pull request.
- Para verificar a cobertura, use `poetry run pytest --cov=api_template --cov-report=html`.

---

Agradecemos suas contribuições para tornar este projeto melhor!

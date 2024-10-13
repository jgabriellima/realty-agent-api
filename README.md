# API Template

## Índice
1. [Introdução](#introdução)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Módulos Principais](#módulos-principais)
    - [Módulo External](#módulo-external)
    - [Módulo Queue](#módulo-queue)
    - [Módulo Celery](#módulo-celery)
4. [Estrutura da API](#estrutura-da-api)
5. [Configuração e Instalação](#configuração-e-instalação)
6. [Configuração](#configuração)
7. [Uso](#uso)
8. [Testes](#testes)
9. [Implantação](#implantação)
10. [Contribuindo](#contribuindo)
11. [Licença](#licença)

## Introdução

API Template é um projeto robusto, escalável e rico em recursos baseado em FastAPI que fornece uma base sólida para a construção de APIs de nível de produção. Ele inclui recursos avançados como integração de API externa, processamento de tarefas assíncronas com Celery e gerenciamento de filas de mensagens.

## Estrutura do Projeto

O projeto segue uma estrutura modular para garantir escalabilidade e manutenibilidade:

```
api-template/
├── api_template/
│   ├── api/
│   │   ├── common/
│   │   └── v1/
│   ├── celery/
│   │   ├── config/
│   │   ├── core/
│   │   ├── monitoring/
│   │   ├── tasks/
│   │   ├── __init__.py
│   │   └── app.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   ├── settings.py
│   │   └── versioning.py
│   ├── db/
│   │   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── external/
│   │   ├── core/
│   │   ├── handlers/
│   │   ├── __init__.py
│   │   ├── example.py
│   │   └── util.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── ratelimit_middleware.py
│   │   ├── request_middleware.py
│   │   ├── security_headers_middleware.py
│   │   └── README.md
│   ├── prompts/
│   │   ├── rag_assistant/
│   │   ├── __init__.py
│   │   ├── example.py
│   │   └── manager.py
│   ├── queue/
│   │   ├── config/
│   │   ├── core/
│   │   ├── handlers/
│   │   ├── __init__.py
│   │   ├── setup.py
│   │   └── README.md
│   ├── tools/
│   │   ├── ai_functions/
│   │   ├── stt/
│   │   ├── tts/
│   │   └── README.md
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── freeze.py
│   │   ├── logging.py
│   │   ├── semantic_search.py
│   │   └── README.md
│   ├── __init__.py
│   └── server.py
├── CODE_QUALITY.md
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── README.md
├── alembic.ini
├── docker-compose.yml
├── entrypoint.sh
├── poetry.lock
├── poetry.toml
├── pyproject.toml
├── pytest.ini
└── requirements.txt
```

### Componentes Principais

- `api_template/`: Contém o código-fonte principal do projeto.
    - `api/`: Implementações da API, incluindo versões e endpoints.
    - `celery/`: Configuração e tarefas do Celery para processamento assíncrono.
    - `config/`: Arquivos de configuração do projeto.
    - `db/`: Modelos de banco de dados e configuração de sessão.
    - `external/`: Integrações com serviços externos.
    - `middleware/`: Middlewares para processamento de requisições.
    - `prompts/`: Gerenciamento de prompts, incluindo assistente RAG.
    - `queue/`: Implementação de sistema de filas.
    - `tools/`: Ferramentas diversas, incluindo funções de IA, STT e TTS.
    - `utils/`: Utilitários gerais do projeto.
    - `server.py`: Ponto de entrada principal da aplicação.

- Arquivos na raiz:
    - `CODE_QUALITY.md`: Diretrizes de qualidade de código.
    - `CONTRIBUTING.md`: Guia para contribuições ao projeto.
    - `Dockerfile`: Configuração para construção da imagem Docker.
    - `LICENSE`: Licença do projeto.
    - `README.md`: Documentação principal do projeto.
    - `alembic.ini`: Configuração do Alembic para migrações de banco de dados.
    - `docker-compose.yml`: Configuração para orquestração de containers.
    - `entrypoint.sh`: Script de entrada para o container Docker.
    - `poetry.lock` e `pyproject.toml`: Gerenciamento de dependências com Poetry.
    - `pytest.ini`: Configuração para testes com pytest.
    - `requirements.txt`: Lista de dependências do projeto (gerada pelo Poetry).

## Módulos Principais

### Módulo External

O módulo `external` fornece um framework flexível para integrar APIs externas em sua aplicação. Ele usa especificações OpenAPI para gerar dinamicamente interfaces de cliente para serviços externos.

Principais características:
- Autodescoberta de manipuladores de API
- Adaptador de API genérico para execução de operações baseadas em especificações OpenAPI
- Funcionalidade de pesquisa semântica para encontrar operações de API relevantes

Exemplo de uso:

```python
from api_template.external.core.setup import APISetup

api_setup = APISetup()
handler = api_setup.get_handler("ExampleHandler")
response = handler.execute_operation("operation_id", params={}, data={})
```

### Módulo Queue

O módulo `queue` implementa um sistema robusto de filas de mensagens, atualmente suportando RabbitMQ. Ele fornece uma interface de alto nível para publicação e consumo de mensagens em toda a sua aplicação.

Principais características:
- Processamento assíncrono de mensagens
- Suporte a Dead Letter Queue (DLQ)
- Funcionalidade de verificação de integridade
- Implementação do padrão Circuit breaker

Exemplo de uso:
```python
from api_template.queue.core.manager.queue_manager import queue_manager

publisher = queue_manager.get_publisher("queue_name")
await publisher.publish_message("queue_name", {"type": "message_type", "content": "message_content"})
```

### Módulo Celery

O módulo `celery` integra o Celery para processamento e agendamento de tarefas assíncronas. Ele fornece uma estrutura para definir, executar e monitorar tarefas em segundo plano.

Principais características:
- Mecanismos de repetição e recuo de tarefas
- Registro e monitoramento de tarefas
- Integração com vários tipos de broker (RabbitMQ, Redis, etc.)
- Celery Beat para agendamento de tarefas

Exemplo de uso:
```python
from api_template.celery.tasks.general_tasks import CreateUserTask

result = CreateUserTask().delay("task_parameter")
```

## Estrutura da API

A API segue uma estrutura versionada, com a versão atual sendo v1. Ela usa FastAPI para roteamento e manipulação de requisições. A API é projetada com uma abordagem de arquitetura limpa, separando as preocupações em diferentes camadas para melhor manutenibilidade e escalabilidade.

### Visão Geral

A estrutura da API é organizada da seguinte forma:

```
api_template/
├── api/
│   ├── v1/
│   │   ├── controllers/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── auth/
│   │   ├── dependencies.py
│   │   └── router.py
│   └── common/
│       ├── errors.py
│       ├── pagination.py
│       └── api_exceptions.py
└── server.py
```

### Componentes Principais

#### 1. Controllers (`api/v1/controllers/`)

Os controllers lidam com requisições e respostas HTTP. Eles são responsáveis por:
- Definir endpoints da API
- Lidar com a validação de requisições
- Chamar os serviços apropriados
- Retornar respostas

Exemplo (`user_controller.py`):
```python
@router.post("/", response_model=UserResponse, status_code=201)
@require_auth
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user)
```

#### 2. Services (`api/v1/services/`)

Os services implementam a lógica de negócios da aplicação. Eles:
- Coordenam entre múltiplos repositórios
- Implementam operações complexas
- Lidam com regras de negócio e validações

Exemplo (`user_service.py`):
```python
class UserService:
    def __init__(self, db):
        self.repository = UserRepository(db)

    async def create_user(self, user: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = get_password_hash(user.password)
        return await self.repository.create(UserCreate(**user.dict(), hashed_password=hashed_password))
```

#### 3. Repositories (`api/v1/repositories/`)

Os repositories gerenciam o acesso e armazenamento de dados. Eles:
- Fazem interface com o banco de dados
- Implementam operações CRUD
- Lidam com a lógica de persistência de dados

Exemplo (`user_repository.py`):
```python
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    async def create(self, user: UserCreate) -> User:
        db_user = User(**user.dict())
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
```

#### 4. Schemas (`api/v1/schemas/`)

Os schemas definem modelos de dados e regras de validação. Eles:
- Especificam a estrutura dos dados de requisição e resposta
- Implementam lógica de validação de dados
- Fornecem serialização/desserialização de dados

Exemplo (`user_schemas.py`):
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True
```

#### 5. Autenticação (`api/v1/auth/`)

O módulo de autenticação lida com a autenticação e autorização do usuário. Ele inclui:
- Geração e validação de tokens
- Lógica de autenticação de usuários
- Decoradores de autorização

Exemplo (`auth.py`):
```python
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
```

#### 6. Dependências (`api/v1/dependencies.py`)

As dependências fornecem componentes reutilizáveis que podem ser injetados em funções de rota. Elas:
- Gerenciam sessões de banco de dados
- Fornecem acesso a serviços e repositórios
- Lidam com tarefas comuns de processamento de requisições

Exemplo:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)
```

#### 7. Router (`api/v1/router.py`)

O router consolida todas as rotas da API e as organiza em uma estrutura coesa. Ele:
- Agrupa endpoints relacionados
- Aplica prefixos e tags comuns
- Organiza rotas por recurso ou funcionalidade

Exemplo:
```python
router = APIRouter(prefix=f"/api/{APIVersion.V1}")
router.include_router(user_controller.router, tags=["Users"])
router.include_router(auth_controller.router, tags=["Authentication"])
```

#### 8. Utilidades Comuns (`api/common/`)

O diretório common contém utilitários compartilhados e classes base usadas em toda a API. Ele inclui:
- Tratamento de erros (`errors.py`)
- Utilitários de paginação (`pagination.py`)
- Exceções personalizadas da API (`api_exceptions.py`)

Esses componentes trabalham juntos para criar uma estrutura de API modular, manutenível e escalável. A separação de preocupações permite fácil teste, refatoração e extensão de funcionalidades.

### Integração com Outros Módulos

A estrutura da API se integra perfeitamente com outros módulos-chave do projeto:

1. **Módulo External**: Os controllers podem usar a classe `APISetup` para interagir com APIs externas.
2. **Módulo Queue**: Os services podem publicar mensagens em filas usando o `queue_manager`.
3. **Módulo Celery**: Controllers ou services podem iniciar tarefas em segundo plano usando funções de tarefa do Celery.

Esta integração permite que a API aproveite todas as capacidades da arquitetura do projeto, mantendo uma estrutura limpa e organizada.

## Configuração e Instalação

1. Clone o repositório:

```bash 
   git clone https://github.com/seu-repo/api-template.git
   cd api-template
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```
cp .env.example .env
# Edite .env com sua configuração
```

4. Execute as migrações do banco de dados:
```
alembic upgrade head
```

5. Inicie o servidor API:
```
uvicorn api_template.server:app --reload
```

## Configuração

A configuração é gerenciada através de variáveis de ambiente e arquivos YAML:

- `.env`: Variáveis específicas do ambiente
- `api_template/queue/config/queues.yaml`: Configuração de filas
- `api_template/celery/config/celery_beat_schedule.yaml`: Agendamento do Celery Beat

## Uso

Após iniciar o servidor, você pode acessar a documentação da API em `http://localhost:8000/docs`.

## Docker

Para rápido setup, considere usar Docker:

```
docker-compose up --build
```

## Ferramentas de Qualidade de Código

Este projeto utiliza várias ferramentas para manter a qualidade e consistência do código. A configuração e uso dessas ferramentas são automatizados através do pre-commit, com exceção dos testes de cobertura.

### Black

Black é um formatador de código Python que aplica um estilo consistente automaticamente.

Configuração (em `pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py39']
```

Para executar o Black manualmente:
```bash
poetry run black .
```

Para verificar sem fazer alterações:
```bash
poetry run black --check .
```

### isort

isort organiza suas importações alfabeticamente e separadamente em seções.

Configuração (em `pyproject.toml`):
```toml
[tool.isort]
profile = "black"
line_length = 100
```


Para executar o isort manualmente:
```bash
poetry run isort .
```

Para verificar sem fazer alterações:
```bash
poetry run isort --check-only .
```

### Flake8

Flake8 verifica seu código Python em busca de erros de estilo e possíveis bugs.

Configuração (em `.flake8`):
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    .venv,
    .eggs,
    *.egg,
    build,
    dist
```

Para executar o Flake8 manualmente:
```bash
poetry run flake8 .
```

### autopep8

autopep8 é usado para corrigir automaticamente muitos dos problemas identificados pelo Flake8.

Para executar o autopep8 manualmente:
```bash
poetry run autopep8 --in-place --aggressive --aggressive -r .
```

Para verificar sem fazer alterações:
```bash
poetry run autopep8 --diff --aggressive --aggressive -r .
```

### Testes de Cobertura

Usamos pytest-cov para gerar relatórios de cobertura de código, que nos ajudam a identificar áreas do código que precisam de mais testes.

#### Executando Testes de Cobertura

Para executar os testes com cobertura:

```bash
poetry run pytest --cov=api_template --cov-report=html
```

Este comando gera um relatório HTML detalhado na pasta `htmlcov`.

#### Quando Executar Testes de Cobertura

1. Durante o desenvolvimento local (regularmente)
2. Antes de criar um pull request
3. Na pipeline de Integração Contínua (CI)
4. Periodicamente (por exemplo, semanalmente) para revisão da equipe

Nota: Os testes de cobertura não são incluídos no pre-commit devido ao tempo de execução.

### Uso Integrado com Pre-commit

Estas ferramentas (exceto os testes de cobertura) são configuradas para serem executadas automaticamente antes de cada commit através do pre-commit. Para executar manualmente todas as verificações:

```bash
poetry run pre-commit run --all-files
```

### Melhores Práticas

1. Execute o pre-commit antes de fazer push para o repositório remoto.
2. Use as ferramentas individualmente durante o desenvolvimento para verificações rápidas.
3. Execute os testes de cobertura regularmente e antes de submeter pull requests.
4. Mantenha as configurações das ferramentas atualizadas e consistentes com as necessidades do projeto.
5. Revise regularmente os relatórios gerados por estas ferramentas para identificar áreas de melhoria no código.


### Documentação Adicional

Para mais detalhes sobre nossas práticas de qualidade de código, consulte:
- [CODE_QUALITY.md](CODE_QUALITY.md): Guia detalhado sobre nossas ferramentas e práticas
- [CONTRIBUTING.md](CONTRIBUTING.md): Diretrizes para contribuidores, incluindo padrões de qualidade


## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

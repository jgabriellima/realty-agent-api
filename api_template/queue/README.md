# Queue System - FastAPI Template

## Descrição

Este projeto é um template para sistemas baseados em filas utilizando FastAPI. Ele suporta múltiplos tipos de filas,
como RabbitMQ, e foi projetado para ser escalável e "production-grade".

## Configuração

### Arquivo YAML de Configuração

As configurações para as filas estão localizadas em um arquivo YAML. Exemplo:

```yaml
queues:
  - name: my_queue
    type: rabbitmq
    broker_url: "localhost"
    port: 5671
    ssl: true
    ssl_context: null  # Configure o contexto SSL conforme necessário
    heartbeat: 600
    enable_consumer: true
    enable_publisher: true
```

## Estrutura do Projeto

1. queue/interfaces.py: Define as interfaces para consumidores, publicadores, processadores e health checks.
2. queue/providers/rabbitmq/: Implementação específica para RabbitMQ.
3. queue/handlers/: Contém os handlers de mensagens para diferentes tipos de filas.
4. queue/setup.py: Configura os canais de filas, incluindo consumidores e publicadores.
5. queue/health_check.py: Gerencia os health checks das filas.

## Usando Dead Letter Queues (DLQs)

As mensagens que falham após várias tentativas são movidas para uma Dead Letter Queue (DLQ) para análise posterior. O
nome da DLQ é baseado no nome da fila original, prefixado com dlq_.

## Extensão para Novos Tipos de Filas

Para adicionar suporte a novos tipos de filas, siga estes passos:

1. Crie uma nova implementação de QueueConsumer, QueuePublisher, QueueProcessor, e QueueHealthCheck para o novo tipo de
   fila.
2. Adicione as novas classes no arquivo setup.py, em get_consumer, get_publisher e get_processor.
3. Atualize o arquivo de configuração YAML para incluir as novas filas.

## Inicializando o Projeto

Para iniciar o projeto, use o seguinte código no seu main.py:

```python
from fastapi import FastAPI
from app.queue.setup import lifespan_handler

app = FastAPI(lifespan=lifespan_handler)
```

Certifique-se de que todas as configurações necessárias estejam definidas no arquivo YAML antes de iniciar o aplicativo.

# Fluxo de Execução do Sistema de Filas

## 1. Setup e Inicialização

1.1. O arquivo `setup.py` é executado durante a inicialização da aplicação FastAPI:

- Carrega as configurações de fila do arquivo `queues.yaml`.
- Cria uma instância de `MessageProcessor`.
- Registra os handlers usando `register_handlers()` de `handlers/register_handlers.py`.

1.2. Para cada fila configurada:

- Cria um consumidor (`AsyncRabbitMQConsumer`) se `enable_consumer` for verdadeiro.
- Cria um publicador (`AsyncRabbitMQPublisher`) se `enable_publisher` for verdadeiro.
- Se `enable_dlq` for verdadeiro, cria um `RabbitMQDeadLetterQueueHandler`.

1.3. Inicia os consumidores em paralelo usando `ThreadPoolExecutor`.

1.4. Configura o gerenciamento do ciclo de vida da aplicação FastAPI usando `lifespan_handler`.

## 2. Publicação de Mensagem

2.1. Quando uma mensagem precisa ser publicada:

- O código chama `publish_message()` do `AsyncRabbitMQPublisher`.

2.2. O método `publish_message()`:

- Usa o `QueueCircuitBreaker` para executar a publicação.
- Obtém uma conexão do `RabbitMQConnectionManager`.
- Publica a mensagem na fila especificada.

Exemplo de publicação:

```python
publisher = AsyncRabbitMQPublisher("user_channel", queue_config)
await publisher.publish_message("user_channel",
                                json.dumps({"type": "send_audio", "user_id": 123, "content": "audio_data"}))
```

## 3. Consumo de Mensagem

3.1. O `AsyncRabbitMQConsumer` está continuamente escutando a fila especificada.

3.2. Quando uma mensagem é recebida:

- O consumidor chama `process_message()`.

3.3. `process_message()`:

- Decodifica a mensagem JSON.
- Extrai o tipo da mensagem.
- Cria um `RabbitMQMessageHandler` para a mensagem.
- Chama `process()` do `MessageProcessor`.

3.4. O `MessageProcessor`:

- Identifica o handler apropriado com base no tipo da mensagem.
- Executa o handler correspondente.

3.5. O handler (por exemplo, `UserHandler.send_audio`):

- Processa a mensagem (por exemplo, notifica o usuário).

3.6. Após o processamento:

- Se bem-sucedido, o `RabbitMQMessageHandler` confirma (ack) a mensagem.
- Se falhar, tenta reprocessar ou move para a DLQ, dependendo da configuração.

Exemplo de consumo:

```python
# Isso acontece internamente no AsyncRabbitMQConsumer
message = {"type": "send_audio", "user_id": 123, "content": "audio_data"}
await consumer.process_message(message)
# Internamente, isso chama o UserHandler.send_audio(message)
```

## 4. Tratamento de Erros e Recuperação

4.1. Se ocorrer um erro durante o processamento:

- O `RabbitMQMessageHandler` tenta reprocessar a mensagem com backoff exponencial.
- Após várias tentativas, move a mensagem para a DLQ.

4.2. O `RabbitMQDeadLetterQueueHandler`:

- Monitora periodicamente a DLQ.
- Tenta reprocessar mensagens da DLQ.

## 5. Verificação de Saúde

5.1. Periodicamente ou sob demanda:

- O endpoint `/health/queue` é chamado.

5.2. Para cada fila configurada:

- `RabbitMQHealthCheck` verifica a conexão com o RabbitMQ.
- Retorna o status de saúde de cada fila.



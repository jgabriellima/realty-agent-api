# Estratégias para Encadeamento de Tarefas no Celery

## 1. Usando Task Signatures e Chains

O Celery oferece uma maneira elegante de encadear tarefas usando signatures e chains.

```python
from celery import chain
from api_template.celery.app import celery_app
from api_template.celery.core.base import BaseTask


@celery_app.task(bind=True, base=BaseTask)
class ProcessOrderTask(BaseTask):
    name = "process_order_task"

    def run(self, order_id):
        # Processar o pedido
        result = f"Pedido {order_id} processado"

        # Encadear com a tarefa de atualização de status
        update_task = UpdateOrderStatusTask().s(order_id, "processed")
        notify_task = NotifyCustomerTask().s(order_id)

        # Executar as tarefas em cadeia
        chain(update_task, notify_task).apply_async()

        return result


@celery_app.task(bind=True, base=BaseTask)
class UpdateOrderStatusTask(BaseTask):
    name = "update_order_status_task"

    def run(self, order_id, status):
        # Atualizar o status do pedido no banco de dados
        return f"Status do pedido {order_id} atualizado para {status}"


@celery_app.task(bind=True, base=BaseTask)
class NotifyCustomerTask(BaseTask):
    name = "notify_customer_task"

    def run(self, order_id):
        # Notificar o cliente sobre o processamento do pedido
        return f"Cliente notificado sobre o pedido {order_id}"
```

## 2. Usando Callbacks

Para cenários onde você precisa executar uma tarefa após a conclusão de outra, mas não necessariamente em uma cadeia,
você pode usar callbacks.

```python
from celery.result import AsyncResult


@celery_app.task(bind=True, base=BaseTask)
class LongRunningTask(BaseTask):
    name = "long_running_task"

    def run(self, data):
        # Processar dados
        result = f"Processamento concluído: {data}"

        # Agendar a tarefa de callback
        CallbackTask().apply_async(args=[result], countdown=10)

        return result


@celery_app.task(bind=True, base=BaseTask)
class CallbackTask(BaseTask):
    name = "callback_task"

    def run(self, result):
        # Fazer algo com o resultado da tarefa anterior
        return f"Callback processado com resultado: {result}"
```

## 3. Usando Groups para Tarefas Paralelas

Se você precisa executar várias tarefas em paralelo e então fazer algo com os resultados, você pode usar Groups.

```python
from celery import group


@celery_app.task(bind=True, base=BaseTask)
class ProcessBatchTask(BaseTask):
    name = "process_batch_task"

    def run(self, batch_ids):
        # Criar um grupo de tarefas para processar cada item do lote
        process_tasks = group(ProcessItemTask().s(item_id) for item_id in batch_ids)

        # Executar as tarefas em paralelo e coletar os resultados
        results = process_tasks.apply_async()

        # Agendar uma tarefa para processar os resultados
        ProcessResultsTask().apply_async(args=[results.id], countdown=60)

        return f"Lote iniciado com {len(batch_ids)} itens"


@celery_app.task(bind=True, base=BaseTask)
class ProcessItemTask(BaseTask):
    name = "process_item_task"

    def run(self, item_id):
        # Processar um item individual
        return f"Item {item_id} processado"


@celery_app.task(bind=True, base=BaseTask)
class ProcessResultsTask(BaseTask):
    name = "process_results_task"

    def run(self, group_result_id):
        # Recuperar os resultados do grupo
        group_result = AsyncResult(group_result_id)
        results = group_result.get()

        # Fazer algo com os resultados
        return f"Processados {len(results)} resultados"
```

## 4. Usando Canvas para Fluxos de Trabalho Complexos

Para fluxos de trabalho mais complexos, o Celery oferece uma API de Canvas que permite combinar chains, groups e chords.

```python
from celery import chain, group, chord


@celery_app.task(bind=True, base=BaseTask)
class InitiateComplexWorkflowTask(BaseTask):
    name = "initiate_complex_workflow_task"

    def run(self, data):
        # Definir o fluxo de trabalho
        workflow = chain(
            PrepareDataTask().s(data),
            group(
                ProcessPartATask().s(),
                ProcessPartBTask().s()
            ),
            chord(
                (FinalizePartATask().s(), FinalizePartBTask().s()),
                AggregateResultsTask().s()
            )
        )

        # Iniciar o fluxo de trabalho
        result = workflow.apply_async()

        return f"Fluxo de trabalho complexo iniciado: {result.id}"

# Definir as outras tarefas (PrepareDataTask, ProcessPartATask, etc.)
```

## 5. Atualizações de Status em Tempo Real

Para cenários onde você precisa atualizar o status de um registro no banco de dados durante o processamento:

```python
@celery_app.task(bind=True, base=BaseTask)
class LongProcessingTask(BaseTask):
    name = "long_processing_task"

    def run(self, record_id):
        # Iniciar processamento
        self.update_status(record_id, "started")

        # Simulação de processamento longo
        for i in range(5):
            time.sleep(10)
            self.update_status(record_id, f"processing_step_{i + 1}")

        # Finalizar processamento
        self.update_status(record_id, "completed")

        return f"Processamento do registro {record_id} concluído"

    def update_status(self, record_id, status):
        UpdateStatusTask().apply_async(args=[record_id, status], priority=9)


@celery_app.task(bind=True, base=BaseTask)
class UpdateStatusTask(BaseTask):
    name = "update_status_task"

    def run(self, record_id, status):
        # Atualizar o status no banco de dados
        return f"Status do registro {record_id} atualizado para {status}"
```
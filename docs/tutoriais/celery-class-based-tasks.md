# Implementação de Tasks Celery Baseadas em Classes

## Objetivo
Garantir que todas as tasks Celery sejam implementadas usando classes, promovendo melhor organização, reutilização de código e manutenibilidade.

## Implementação

### 1. Defina uma classe base para suas tasks

```python
from celery import Task

class BaseTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Lógica comum de tratamento de falhas
        print(f"Task {task_id} failed: {exc}")

    def on_success(self, retval, task_id, args, kwargs):
        # Lógica comum para tasks bem-sucedidas
        print(f"Task {task_id} completed successfully")
```

### 2. Implemente tasks específicas como classes

```python
from your_project.celery_app import celery_app
from your_project.models import User, QueryResult
from your_project.security import security_handler

@celery_app.task(bind=True, base=BaseTask)
class ProcessComplexQueryTask(BaseTask):
    name = "tasks.process_complex_query"

    def run(self, user_id, encrypted_query):
        try:
            # Descriptografar a query
            query = security_handler.decrypt_data(encrypted_query)

            # Processar a query
            result = self.process_query(query)

            # Criptografar o resultado
            encrypted_result = security_handler.encrypt_data(result)

            # Salvar o resultado no banco de dados
            QueryResult.create(user_id=user_id, query=encrypted_query, result=encrypted_result)

            return encrypted_result
        except Exception as e:
            self.retry(exc=e, countdown=60)  # Retry após 1 minuto

    def process_query(self, query):
        # Lógica específica de processamento da query
        pass

@celery_app.task(bind=True, base=BaseTask)
class SendNotificationTask(BaseTask):
    name = "tasks.send_notification"

    def run(self, user_id, encrypted_message):
        try:
            # Descriptografar a mensagem
            message = security_handler.decrypt_data(encrypted_message)

            # Obter o email do usuário
            user = User.get_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Enviar a notificação
            self.send_email(user.email, message)

            return "Notification sent successfully"
        except Exception as e:
            self.retry(exc=e, countdown=30)  # Retry após 30 segundos

    def send_email(self, email, message):
        # Lógica de envio de email
        pass
```

### 3. Uso das tasks no assistente

```python
class IntegratedAssistant(AIAssistant):
    def handle_input(self, user_id, user_input):
        intent = self.get_intent(user_input)
        
        if intent == 'complex_query':
            encrypted_input = security_handler.encrypt_data(user_input)
            task = ProcessComplexQueryTask().delay(user_id, encrypted_input)
            return f"Estou processando sua solicitação. ID da tarefa: {task.id}"
        elif intent == 'notification':
            encrypted_message = security_handler.encrypt_data("Sua consulta foi processada.")
            task = SendNotificationTask().delay(user_id, encrypted_message)
            return "Uma notificação será enviada em breve."
        elif intent == 'simple_query':
            response = self.process_input(user_input)
            self.save_interaction(user_id, user_input, response)
            return response
        else:
            return "Desculpe, não entendi sua solicitação."
```

### 4. Registro e monitoramento de tasks baseadas em classes

```python
from celery.signals import before_task_publish, task_prerun, task_postrun
from prometheus_client import Counter, Histogram
import time

TASK_SUCCESS = Counter('task_success_total', 'Successful task executions', ['task_name'])
TASK_FAILURE = Counter('task_failure_total', 'Failed task executions', ['task_name'])
TASK_DURATION = Histogram('task_duration_seconds', 'Task duration in seconds', ['task_name'])

@before_task_publish.connect
def task_publish_handler(sender=None, headers=None, body=None, **kwargs):
    info = headers if 'task' in headers else body
    print(f'Task {info["id"]} published: {info["task"]}')

@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    task.start_time = time.time()
    print(f'Task {task_id} started: {task.name}')

@task_postrun.connect
def task_postrun_handler(task_id, task, *args, retval=None, state=None, **kwargs):
    duration = time.time() - task.start_time
    TASK_DURATION.labels(task_name=task.name).observe(duration)
    
    if state == 'SUCCESS':
        TASK_SUCCESS.labels(task_name=task.name).inc()
        print(f'Task {task_id} completed successfully: {task.name}')
    elif state == 'FAILURE':
        TASK_FAILURE.labels(task_name=task.name).inc()
        print(f'Task {task_id} failed: {task.name}')
```

## Benefícios das Tasks Baseadas em Classes

1. **Organização**: Agrupa lógica relacionada em uma única classe.
2. **Reutilização**: Permite herança e compartilhamento de funcionalidades comuns.
3. **Manutenibilidade**: Facilita a adição de novos comportamentos e a modificação de existentes.
4. **Testabilidade**: Torna mais fácil escrever testes unitários para tasks individuais.
5. **Flexibilidade**: Permite a definição de métodos auxiliares dentro da classe da task.

## Melhores Práticas

1. Use uma classe base comum para compartilhar funcionalidades entre tasks.
2. Implemente métodos `on_success` e `on_failure` para tratamento adequado de resultados.
3. Utilize o decorador `@celery_app.task(bind=True, base=BaseTask)` para registrar suas classes como tasks.
4. Mantenha a lógica principal da task no método `run`.
5. Use métodos adicionais na classe para dividir a lógica em partes menores e mais gerenciáveis.
6. Implemente retry logic apropriada para lidar com falhas temporárias.
7. Use o atributo `name` para definir nomes claros e consistentes para suas tasks.

Ao seguir estas diretrizes para implementação de tasks baseadas em classes, você garantirá um código mais organizado, manutenível e robusto para seu sistema de assistente de IA integrado com Celery.

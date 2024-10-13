from celery import Task

from api_template.celery.core.decorators import task_logging


class BaseTask(Task):
    abstract = True

    max_retries = 5
    default_retry_delay = 60  # Define o tempo de espera padrão (em segundos) entre as tentativas de execução. Neste caso, 60 segundos ou 1 minuto.
    rate_limit = "10/m"  # Limita a execução da tarefa a 10 vezes por minuto

    retry_backoff = True  # Ativa o backoff exponencial para as tentativas. Isso significa que o tempo de espera entre as tentativas aumentará exponencialmente
    retry_backoff_max = 600  # Define o tempo máximo de backoff em 600 segundos
    retry_jitter = True  # Adiciona um componente aleatório ao tempo de espera entre as tentativas para evitar que todas as tarefas sejam retentadas simultaneamente

    autoretry_for = (
        Exception,
    )  # Especifica que a tarefa deve ser automaticamente retentada para qualquer exceção

    @task_logging
    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the run method")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        super().on_success(retval, task_id, args, kwargs)

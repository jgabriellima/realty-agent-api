import asyncio

from api_template.queue.core.manager.interfaces import QueueMessageHandler
from api_template.utils.logging import log_message


class RabbitMQMessageHandler(QueueMessageHandler):
    def __init__(self, channel, message, max_retries=5, initial_backoff=1):
        """
        O `message` agora é o objeto da mensagem que vem do RabbitMQ e tem os métodos ack/nack.
        """
        self.channel = channel
        self.message = message  # Substituímos method pelo próprio message
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff

    async def ack(self):
        """Acknowledges the message using the ack method of the message itself."""
        log_message(
            "message_processed", self.message.routing_key, message=self.message.body.decode()
        )

    async def nack(self, requeue=False):
        """Negatively acknowledges the message using the nack method of the message."""
        await self.message.nack(
            requeue=requeue
        )  # Rejeita a mensagem e, opcionalmente, a reencaminha
        log_message(
            "message_rejected", self.message.routing_key, message=self.message.body.decode()
        )

    async def retry(self, retries=0):
        """Retries the message with exponential backoff."""
        if retries < self.max_retries:
            backoff = self.initial_backoff * (2**retries)
            await asyncio.sleep(backoff)
            await self.message.nack(
                requeue=True
            )  # Reencaminha a mensagem para a fila após o backoff
            log_message(
                "message_retry",
                self.message.routing_key,
                error=f"Retrying message with backoff {backoff}. Retries left: {self.max_retries - retries - 1}",
            )
        else:
            await self.message.nack(requeue=False)  # Move para DLQ se os retries se esgotarem
            log_message(
                "message_dlq",
                self.message.routing_key,
                error="Message moved to Dead Letter Queue after max retries.",
            )

from circuitbreaker import circuit


class QueueCircuitBreaker:
    @circuit(failure_threshold=5, recovery_timeout=30)
    async def execute(self, func, *args, **kwargs):
        return await func(*args, **kwargs)

import logging
import threading

import aio_pika

logger = logging.getLogger(__name__)


class RabbitMQConnectionManager:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, queue_name, queue_config):
        with cls._lock:
            if queue_name not in cls._instances:
                instance = super(RabbitMQConnectionManager, cls).__new__(cls)
                instance._initialize(queue_config)
                cls._instances[queue_name] = instance
            return cls._instances[queue_name]

    def _initialize(self, queue_config):
        self._queue_config = queue_config
        self._connection_pool = []
        self._max_pool_size = 10
        self._initialized = False

    async def initialize_connections(self):
        """
        Initializes the connections pool.
        :return:
        """
        if not self._initialized:
            await self._create_async_connections()
            self._initialized = True

    async def _create_new_async_connection(self):
        """
        Creates a new connection to RabbitMQ.
        :return:
        """
        try:
            connection = await aio_pika.connect_robust(
                host=self._queue_config.broker_url,
                port=self._queue_config.port,
                login=self._queue_config.username,
                password=self._queue_config.password,
                heartbeat=self._queue_config.heartbeat,
                ssl_context=self._queue_config.ssl_context,
            )
            logger.info("New connection established with RabbitMQ")
            return connection
        except Exception as e:
            logger.error(f"Failed to create new connection: {e}")
            raise

    async def _create_async_connections(self):
        """
        Creates a pool of connections to RabbitMQ.
        :return:
        """
        for _ in range(self._max_pool_size):
            connection = await self._create_new_async_connection()
            self._connection_pool.append(connection)

    async def get_async_connection(self):
        """
        Get a connection from the pool.
        :return:
        """
        try:
            if self._connection_pool:
                connection = self._connection_pool.pop(0)
                if connection.is_closed:
                    logger.warning("Connection is closed, creating a new connection.")
                    connection = await self._create_new_async_connection()
                return connection
            else:
                logger.warning("Async connection pool is empty, creating a new connection.")
                return await self._create_new_async_connection()
        except Exception as e:
            logger.error(f"Error while getting connection: {e}")
            raise

    async def release_async_connection(self, connection):
        """
        Release a connection back to the pool.
        :param connection:
        :return:
        """
        try:
            if len(self._connection_pool) < self._max_pool_size and not connection.is_closed:
                self._connection_pool.append(connection)
            else:
                await connection.close()
        except Exception as e:
            logger.error(f"Error while releasing connection: {e}")

    async def close_all_connections(self):
        """
        Close all connections in the pool.
        :return:
        """
        while self._connection_pool:
            connection = self._connection_pool.pop()
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

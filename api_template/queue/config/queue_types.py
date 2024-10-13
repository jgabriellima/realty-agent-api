from enum import Enum


class QueueType(Enum):
    KAFKA = "kafka"
    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    SQS = "sqs"
    # Add here the new queue type supported

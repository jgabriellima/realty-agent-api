from api_template.config.settings import settings

broker_api = settings.CELERY_BROKER_URL
max_tasks = 10000
persistent = True
db = "flower.db"

import logging
from time import sleep


class APIHealthCheck:
    def __init__(self, api_manager, retry_count=3, retry_interval=5):
        self.api_manager = api_manager
        self.retry_count = retry_count
        self.retry_interval = retry_interval

    def check_health(self):
        for api_name in self.api_manager.list_apis():
            success = self._retry_health_check(api_name)
            if success:
                logging.info(f"API {api_name} is healthy.")
            else:
                logging.error(f"API {api_name} health check failed after retries.")

    def _retry_health_check(self, api_name):
        for attempt in range(self.retry_count):
            try:
                self.api_manager.execute_operation(api_name, "/")
                return True
            except Exception as e:
                logging.error(f"API {api_name} health check attempt {attempt + 1} failed: {e}")
                sleep(self.retry_interval)
        return False

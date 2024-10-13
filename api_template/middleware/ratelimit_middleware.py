import hashlib
import ipaddress
import time

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, period: int, hash_ips: bool = False):
        super().__init__(app)
        self.max_requests = max_requests
        self.period = period
        self.hash_ips = hash_ips
        self.requests = {}

    def get_client_ip(self, request: Request) -> str:
        # Retrieve the client's IP address
        client_ip = request.client.host
        try:
            # Validate IP (handles both IPv4 and IPv6)
            ipaddress.ip_address(client_ip)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid IP address")

        # Optionally hash the IP address for privacy
        if self.hash_ips:
            client_ip = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()

        return client_ip

    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        current_time = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Filter out requests that are outside the current time period
        self.requests[client_ip] = [
            req for req in self.requests[client_ip] if req > current_time - self.period
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Too many requests")

        self.requests[client_ip].append(current_time)

        return await call_next(request)

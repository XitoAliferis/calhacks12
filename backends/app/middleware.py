#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   middleware.py
@Time    :   2025/10/25 15:55:38
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   custom FastAPI middleware utilities.
'''


from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, DefaultDict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# rate limiter middleware.
class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Naive in-memory rate limiter suitable for local/dev usage."""
    # initializing the rate limiter.
    def __init__(self, app, limit: int, window_seconds: int) -> None:  # type: ignore[override]
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self._hits: DefaultDict[str, Deque[float]] = defaultdict(deque)

    # dispatching the request.
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        if self.limit <= 0:
            return await call_next(request)
        # getting the key for the request.
        key = request.client.host if request.client else "global"
        # getting the current time.
        now = time.monotonic()
        window_start = now - self.window
        # getting the bucket for the request.
        bucket = self._hits[key]
        # removing old hits from the bucket.
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        # checking if the rate limit has been exceeded.
        if len(bucket) >= self.limit:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        bucket.append(now)
        # calling the next middleware.
        return await call_next(request)

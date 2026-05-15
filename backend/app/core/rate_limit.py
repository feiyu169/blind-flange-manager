"""速率限制中间件"""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        # 存储请求记录：{ip: [(timestamp, path), ...]}
        self.request_records: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求"""
        # 测试环境禁用速率限制
        if settings.DEBUG:
            return await call_next(request)

        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"

        # 检查是否是登录接口
        if request.url.path == "/api/v1/users/login" and request.method == "POST":
            # 对登录接口应用更严格的限制
            if not await self._check_login_rate_limit(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="登录尝试过于频繁，请稍后再试",
                )
        else:
            # 对其他接口应用通用限制
            if not await self._check_general_rate_limit(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后再试",
                )

        # 记录请求
        self._record_request(client_ip, request.url.path)

        # 处理请求
        response = await call_next(request)
        return response

    async def _check_login_rate_limit(self, client_ip: str) -> bool:
        """检查登录接口速率限制"""
        now = time.time()
        records = self.request_records.get(client_ip, [])

        # 清理过期记录
        records = [r for r in records if now - r[0] < 3600]  # 保留1小时内的记录

        # 检查每分钟限制（登录接口更严格：每分钟5次）
        minute_records = [r for r in records if now - r[0] < 60]
        if len(minute_records) >= 5:
            return False

        # 检查每小时限制（登录接口更严格：每小时20次）
        hour_records = [r for r in records if now - r[0] < 3600]
        if len(hour_records) >= 20:
            return False

        return True

    async def _check_general_rate_limit(self, client_ip: str) -> bool:
        """检查通用速率限制"""
        now = time.time()
        records = self.request_records.get(client_ip, [])

        # 清理过期记录
        records = [r for r in records if now - r[0] < 3600]  # 保留1小时内的记录

        # 检查每分钟限制
        minute_records = [r for r in records if now - r[0] < 60]
        if len(minute_records) >= self.requests_per_minute:
            return False

        # 检查每小时限制
        hour_records = [r for r in records if now - r[0] < 3600]
        if len(hour_records) >= self.requests_per_hour:
            return False

        return True

    def _record_request(self, client_ip: str, path: str) -> None:
        """记录请求"""
        now = time.time()
        self.request_records[client_ip].append((now, path))

        # 清理过期记录（保留1小时）
        self.request_records[client_ip] = [
            r for r in self.request_records[client_ip]
            if now - r[0] < 3600
        ]

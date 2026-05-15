"""盲板管理系统 - FastAPI 应用入口"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动时
    yield
    # 关闭时
    await engine.dispose()


app = FastAPI(
    title="盲板管理系统 API",
    description="工业管道法兰盲板管理系统后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查"""
    return {"status": "ok", "version": "0.1.0"}


# API 路由注册
from app.api.v1.user import router as user_router
from app.api.v1.blind_flange import router as blind_flange_router
from app.api.v1.scan import router as scan_router
from app.api.v1.workflow import router as workflow_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.inspection import router as inspection_router
from app.api.v1.dashboard import router as dashboard_router

app.include_router(user_router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(blind_flange_router, prefix="/api/v1/blind-flanges", tags=["盲板管理"])
app.include_router(scan_router, prefix="/api/v1/scan", tags=["扫码"])
app.include_router(workflow_router, prefix="/api/v1/workflows", tags=["流程管理"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["库存管理"])
app.include_router(inspection_router, prefix="/api/v1/inspections", tags=["巡检"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["仪表盘"])

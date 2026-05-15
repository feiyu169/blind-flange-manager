"""扫码 API"""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.blind_flange import BlindFlangeResponse
from app.schemas.scan_log import ScanLogResponse
from app.services.auth import get_current_user
from app.services.scan import ScanService

router = APIRouter()


@router.get("/history", response_model=List[ScanLogResponse])
async def get_scan_history(
    user_id: int = Query(None, description="用户 ID"),
    blind_flange_id: int = Query(None, description="盲板 ID"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取扫码历史"""
    scan_service = ScanService(db)
    logs = await scan_service.get_scan_history(user_id, blind_flange_id, limit)
    return [ScanLogResponse.model_validate(log) for log in logs]


@router.get("/{code}", response_model=BlindFlangeResponse)
async def scan_blind_flange(
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """扫码获取盲板信息"""
    scan_service = ScanService(db)
    blind_flange = await scan_service.scan(code, current_user.id)
    return BlindFlangeResponse.model_validate(blind_flange)


@router.get("/{code}/qrcode")
async def get_qrcode(
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取二维码图片（按需生成）"""
    scan_service = ScanService(db)
    return await scan_service.get_qrcode(code)

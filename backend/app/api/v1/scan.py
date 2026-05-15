"""扫码 API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.blind_flange import BlindFlangeResponse
from app.services.auth import get_current_user
from app.services.blind_flange import get_blind_flange_by_code, get_status_logs
from app.utils.qrcode import generate_qrcode

router = APIRouter()


@router.get("/{code}", response_model=BlindFlangeResponse)
async def scan_blind_flange(
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """扫码获取盲板信息"""
    blind_flange = await get_blind_flange_by_code(db, code)
    return BlindFlangeResponse.model_validate(blind_flange)


@router.get("/{code}/qrcode")
async def get_qrcode(
    code: str,
    current_user: User = Depends(get_current_user),
):
    """获取二维码图片（按需生成）"""
    return generate_qrcode(code)

"""扫码服务"""

import io
from typing import Optional

import qrcode
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.scan_log import ScanLog


class ScanService:
    """扫码服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def scan(self, code: str, user_id: int) -> BlindFlange:
        """扫码查询盲板"""
        # 查询盲板
        result = await self.db.execute(
            select(BlindFlange).where(BlindFlange.code == code)
        )
        blind_flange = result.scalar_one_or_none()

        # 记录扫码日志
        if blind_flange:
            await self._log_scan(blind_flange.id, user_id, True)
            return blind_flange
        else:
            await self._log_scan(None, user_id, False, f"盲板编码 {code} 不存在")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"盲板编码 {code} 不存在",
            )

    async def get_qrcode(self, code: str) -> StreamingResponse:
        """获取二维码图片"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(code)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)

        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=qrcode_{code}.png"},
        )

    async def _log_scan(
        self,
        blind_flange_id: Optional[int],
        user_id: int,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """记录扫码日志"""
        log = ScanLog(
            blind_flange_id=blind_flange_id,
            user_id=user_id,
            success=success,
            error_message=error_message,
        )
        self.db.add(log)
        await self.db.flush()

    async def get_scan_history(
        self,
        user_id: Optional[int] = None,
        blind_flange_id: Optional[int] = None,
        limit: int = 50,
    ) -> list[ScanLog]:
        """获取扫码历史"""
        query = select(ScanLog).order_by(ScanLog.scanned_at.desc())

        if user_id:
            query = query.where(ScanLog.user_id == user_id)
        if blind_flange_id:
            query = query.where(ScanLog.blind_flange_id == blind_flange_id)

        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

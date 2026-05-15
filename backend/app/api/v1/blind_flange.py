"""盲板 API"""

import io
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.blind_flange import (
    BlindFlangeCreate,
    BlindFlangeImportResponse,
    BlindFlangeListResponse,
    BlindFlangeResponse,
    BlindFlangeStatusLogResponse,
    BlindFlangeUpdate,
)
from app.services.auth import get_current_user
from app.services.blind_flange import (
    create_blind_flange,
    delete_blind_flange,
    export_blind_flanges,
    get_blind_flange,
    get_status_logs,
    import_blind_flanges,
    list_blind_flanges,
    update_blind_flange,
)

router = APIRouter()


@router.post("", response_model=BlindFlangeResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: BlindFlangeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建盲板"""
    blind_flange = await create_blind_flange(db, data, current_user.id)
    return BlindFlangeResponse.model_validate(blind_flange)


@router.get("", response_model=BlindFlangeListResponse)
async def list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取盲板列表"""
    result = await list_blind_flanges(db, page, page_size, status, keyword)
    return BlindFlangeListResponse(
        items=[BlindFlangeResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/{blind_flange_id}", response_model=BlindFlangeResponse)
async def get(
    blind_flange_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取盲板详情"""
    blind_flange = await get_blind_flange(db, blind_flange_id)
    return BlindFlangeResponse.model_validate(blind_flange)


@router.put("/{blind_flange_id}", response_model=BlindFlangeResponse)
async def update(
    blind_flange_id: int,
    data: BlindFlangeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新盲板"""
    blind_flange = await update_blind_flange(db, blind_flange_id, data, current_user.id)
    return BlindFlangeResponse.model_validate(blind_flange)


@router.delete("/{blind_flange_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    blind_flange_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除盲板"""
    await delete_blind_flange(db, blind_flange_id)


@router.get("/{blind_flange_id}/status-logs", response_model=List[BlindFlangeStatusLogResponse])
async def get_logs(
    blind_flange_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取状态变更日志"""
    logs = await get_status_logs(db, blind_flange_id)
    return [BlindFlangeStatusLogResponse.model_validate(log) for log in logs]


@router.post("/import", response_model=BlindFlangeImportResponse)
async def import_excel(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量导入盲板"""
    result = await import_blind_flanges(db, file, current_user.id)
    return result


@router.get("/export/excel")
async def export_excel(
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """导出盲板"""
    output = await export_blind_flanges(db, status)
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=blind_flanges.xlsx"},
    )

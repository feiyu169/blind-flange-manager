"""用户 API"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.auth import get_current_user, login, require_roles

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def user_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户登录"""
    return await login(db, login_data)


@router.post("/init-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def init_admin(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """初始化管理员用户（仅当没有用户时可用）"""
    # 检查是否已有用户
    result = await db.execute(select(func.count()).select_from(User))
    count = result.scalar()
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统已有用户，无法使用初始化接口",
        )

    # 创建管理员用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name or "管理员",
        role="admin",
        phone=user_data.phone,
        email=user_data.email,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息"""
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.flush()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post("/me/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    from datetime import datetime

    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误",
        )

    # 更新密码和密码修改时间
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.password_changed_at = datetime.utcnow()
    await db.flush()

    return {"message": "密码修改成功"}


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: str = Query(None, description="角色筛选"),
    keyword: str = Query(None, description="关键词搜索"),
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表（管理员）"""
    query = select(User)

    # 角色筛选
    if role:
        query = query.where(User.role == role)

    # 关键词搜索
    if keyword:
        query = query.where(
            User.username.ilike(f"%{keyword}%")
            | User.real_name.ilike(f"%{keyword}%")
            | User.phone.ilike(f"%{keyword}%")
        )

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """创建用户（管理员）"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        role=user_data.role,
        phone=user_data.phone,
        email=user_data.email,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """获取用户详情（管理员）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """更新用户（管理员）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """删除用户（管理员）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己",
        )

    # 软删除（设置为不活跃）
    user.is_active = False
    await db.flush()

    return None

"""令牌吊销服务"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.models.token_blacklist import TokenBlacklist


async def revoke_token(
    db: AsyncSession,
    token: str,
    user_id: int,
    reason: str,
) -> None:
    """吊销令牌"""
    # 解码令牌获取过期时间
    payload = decode_access_token(token)
    if payload is None:
        return

    exp = payload.get("exp")
    if exp is None:
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expires_at = datetime.fromtimestamp(exp)

    # 添加到黑名单
    blacklist = TokenBlacklist(
        token=token,
        user_id=user_id,
        reason=reason,
        expires_at=expires_at,
    )
    db.add(blacklist)
    await db.flush()


async def is_token_revoked(
    db: AsyncSession,
    token: str,
) -> bool:
    """检查令牌是否被吊销"""
    result = await db.execute(
        select(TokenBlacklist)
        .where(TokenBlacklist.token == token)
    )
    return result.scalar_one_or_none() is not None


async def is_token_valid_for_user(
    db: AsyncSession,
    token: str,
    user_id: int,
    password_changed_at: Optional[datetime],
) -> bool:
    """检查令牌是否对用户有效（考虑密码修改时间）"""
    # 首先检查令牌是否在黑名单中
    if await is_token_revoked(db, token):
        return False

    # 如果密码已修改，检查令牌签发时间是否在密码修改时间之后
    if password_changed_at:
        payload = decode_access_token(token)
        if payload is None:
            return False

        # 获取令牌签发时间（iat）
        iat = payload.get("iat")
        if iat:
            token_issued_at = datetime.fromtimestamp(iat)
            if token_issued_at < password_changed_at:
                return False

    return True


async def cleanup_expired_blacklist(
    db: AsyncSession,
) -> int:
    """清理过期的黑名单记录"""
    result = await db.execute(
        select(TokenBlacklist)
        .where(TokenBlacklist.expires_at < datetime.utcnow())
    )
    expired = result.scalars().all()

    for item in expired:
        await db.delete(item)

    await db.flush()
    return len(expired)

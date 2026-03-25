from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.db.session import get_db_session
from app.models.user import User
from app.models.workspace import Membership, Workspace
from app.services.security import decode_access_token

SessionDep = Annotated[object, Depends(get_db_session)]
bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: SessionDep,
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已失效") from exc

    result = await session.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_workspace(
    session: SessionDep,
    user: CurrentUserDep,
    workspace_id: Annotated[str | None, Header(alias="X-Workspace-Id")] = None,
) -> Workspace:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少工作区头信息")
    membership_result = await session.execute(
        select(Membership).where(Membership.workspace_id == workspace_id, Membership.user_id == user.id)
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None and not user.is_system_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问当前工作区")

    workspace_result = await session.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = workspace_result.scalar_one_or_none()
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工作区不存在")
    return workspace


CurrentWorkspaceDep = Annotated[Workspace, Depends(get_current_workspace)]


def ensure_system_admin(user: CurrentUserDep) -> User:
    if not user.is_system_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅系统管理员可操作")
    return user


SystemAdminDep = Annotated[User, Depends(ensure_system_admin)]

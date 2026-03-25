from fastapi import APIRouter, HTTPException
from sqlalchemy import or_, select

from app.api.deps import SessionDep
from app.models.billing import CreditWallet
from app.models.user import User
from app.models.workspace import Membership, Workspace
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPayload
from app.schemas.common import APIResponse
from app.schemas.workspace import WorkspaceSummary
from app.services.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=APIResponse[TokenPayload])
async def register(payload: RegisterRequest, session: SessionDep):
    exists = await session.execute(
        select(User).where(or_(User.username == payload.username, User.email == payload.email))
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="用户名或邮箱已存在")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    await session.flush()

    workspace = Workspace(name=payload.workspace_name, owner_user_id=user.id)
    session.add(workspace)
    await session.flush()

    session.add(Membership(workspace_id=workspace.id, user_id=user.id, role="owner"))
    session.add(CreditWallet(workspace_id=workspace.id, balance=0, frozen_balance=0))
    await session.commit()

    return APIResponse(
        data=TokenPayload(
            access_token=create_access_token(user.id),
            user={"id": user.id, "username": user.username, "email": user.email, "is_system_admin": False},
            workspace=WorkspaceSummary(id=workspace.id, name=workspace.name, role="owner").model_dump(),
        )
    )


@router.post("/login", response_model=APIResponse[TokenPayload])
async def login(payload: LoginRequest, session: SessionDep):
    result = await session.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    workspace_data = None
    membership_result = await session.execute(select(Membership).where(Membership.user_id == user.id))
    membership = membership_result.scalars().first()
    if membership:
        workspace_result = await session.execute(select(Workspace).where(Workspace.id == membership.workspace_id))
        workspace = workspace_result.scalar_one()
        workspace_data = WorkspaceSummary(id=workspace.id, name=workspace.name, role=membership.role).model_dump()

    return APIResponse(
        data=TokenPayload(
            access_token=create_access_token(user.id),
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_system_admin": user.is_system_admin,
            },
            workspace=workspace_data,
        )
    )

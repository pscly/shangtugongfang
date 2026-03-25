from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.workspace import Membership, Workspace
from app.schemas.common import APIResponse

router = APIRouter(tags=["system"])


@router.get("/api/me", response_model=APIResponse[dict])
async def me(user: CurrentUserDep):
    return APIResponse(
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_system_admin": user.is_system_admin,
        }
    )


@router.get("/api/workspaces", response_model=APIResponse[list[dict]])
async def workspaces(session: SessionDep, user: CurrentUserDep):
    result = await session.execute(select(Membership).where(Membership.user_id == user.id))
    memberships = result.scalars().all()
    payload: list[dict] = []
    for membership in memberships:
        workspace_result = await session.execute(
            select(Workspace).where(Workspace.id == membership.workspace_id)
        )
        workspace = workspace_result.scalar_one()
        payload.append({"id": workspace.id, "name": workspace.name, "role": membership.role})
    return APIResponse(data=payload)

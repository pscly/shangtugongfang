from fastapi import APIRouter

from app.schemas.common import APIResponse

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=APIResponse[dict])
async def healthcheck():
    return APIResponse(data={"status": "ok"})

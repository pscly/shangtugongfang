from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUserDep, CurrentWorkspaceDep, SessionDep
from app.models.job import Job, JobItem
from app.models.product import Product
from app.schemas.common import APIResponse
from app.schemas.job import JobCreateRequest, JobResponse
from app.schemas.pricing import PricingEstimateRequest
from app.services.billing import BillingService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=APIResponse[JobResponse])
async def create_job(
    payload: JobCreateRequest,
    session: SessionDep,
    workspace: CurrentWorkspaceDep,
    user: CurrentUserDep,
):
    product_result = await session.execute(
        select(Product).where(Product.id == payload.product_id, Product.workspace_id == workspace.id)
    )
    product = product_result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    estimate = BillingService.estimate_request(
        PricingEstimateRequest(platform=payload.platform, items=[item.model_dump() for item in payload.items])
    )
    job = Job(
        workspace_id=workspace.id,
        product_id=payload.product_id,
        platform=payload.platform,
        status="queued",
        credits_estimated=estimate.total_credits,
        credits_frozen=estimate.total_credits,
        created_by=user.id,
    )
    session.add(job)
    await session.flush()
    await BillingService.hold_credits(
        session,
        workspace_id=workspace.id,
        amount=estimate.total_credits,
        user_id=user.id,
        related_entity_id=job.id,
    )

    for item, estimate_item in zip(payload.items, estimate.items, strict=False):
        session.add(
            JobItem(
                job_id=job.id,
                category=item.category,
                prompt_draft_id=item.prompt_draft_id,
                provider_model=item.model_key,
                params=item.model_dump(),
                pricing_snapshot=estimate_item.formula.model_dump(),
                credits_estimated=estimate_item.credits,
            )
        )

    await session.commit()
    await session.refresh(job)
    return APIResponse(
        data=JobResponse(
            id=job.id,
            status=job.status,
            credits_estimated=job.credits_estimated,
            credits_frozen=job.credits_frozen,
        )
    )

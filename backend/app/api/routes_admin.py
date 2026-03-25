from fastapi import APIRouter

from app.api.deps import SessionDep, SystemAdminDep
from app.schemas.billing import RechargeCardBatchCreateRequest, RechargeCardBatchResponse, RechargeCardResponse
from app.schemas.common import APIResponse
from app.services.billing import BillingService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/recharge-card-batches", response_model=APIResponse[RechargeCardBatchResponse])
async def create_recharge_batch(
    payload: RechargeCardBatchCreateRequest,
    session: SessionDep,
    admin: SystemAdminDep,
):
    batch, cards = await BillingService.create_recharge_batch(
        session,
        name=payload.name,
        credits_amount=payload.credits_amount,
        total_count=payload.total_count,
        created_by=admin.id,
    )
    await session.commit()
    return APIResponse(
        data=RechargeCardBatchResponse(
            id=batch.id,
            name=batch.name,
            credits_amount=batch.credits_amount,
            total_count=batch.total_count,
            cards=[
                RechargeCardResponse(
                    id=card.id,
                    card_code=card.card_code,
                    credits_amount=card.credits_amount,
                    status=card.status,
                )
                for card in cards
            ],
        )
    )

from fastapi import APIRouter

from app.schemas.common import APIResponse
from app.schemas.pricing import PricingEstimateRequest, PricingEstimateResponse
from app.services.billing import BillingService

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.post("/estimate", response_model=APIResponse[PricingEstimateResponse])
async def estimate_pricing(payload: PricingEstimateRequest):
    return APIResponse(data=BillingService.estimate_request(payload))

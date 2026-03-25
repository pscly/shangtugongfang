from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUserDep, CurrentWorkspaceDep, SessionDep
from app.models.billing import CreditWallet
from app.schemas.billing import RechargeRedeemRequest, RechargeRedeemResponse, WalletResponse
from app.schemas.common import APIResponse
from app.services.billing import BillingService

router = APIRouter(prefix="/api/credits", tags=["credits"])


@router.get("/balance", response_model=APIResponse[WalletResponse])
async def get_balance(session: SessionDep, workspace: CurrentWorkspaceDep, _: CurrentUserDep):
    result = await session.execute(select(CreditWallet).where(CreditWallet.workspace_id == workspace.id))
    wallet = result.scalar_one_or_none()
    if wallet is None:
        raise HTTPException(status_code=404, detail="钱包不存在")
    return APIResponse(data=WalletResponse(balance=wallet.balance, frozen_balance=wallet.frozen_balance))


@router.post("/recharge-cards/redeem", response_model=APIResponse[RechargeRedeemResponse])
async def redeem_recharge_card(
    payload: RechargeRedeemRequest,
    session: SessionDep,
    workspace: CurrentWorkspaceDep,
    user: CurrentUserDep,
):
    wallet_snapshot, card = await BillingService.redeem_card(
        session,
        workspace_id=workspace.id,
        card_code=payload.card_code,
        user_id=user.id,
    )
    await session.commit()
    return APIResponse(
        data=RechargeRedeemResponse(
            wallet=WalletResponse(
                balance=wallet_snapshot.balance,
                frozen_balance=wallet_snapshot.frozen_balance,
            ),
            card_status=card.status,
        )
    )

from dataclasses import dataclass
from secrets import token_hex

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import CreditLedger, CreditWallet, RechargeCard, RechargeCardBatch, RechargeRedemption
from app.schemas.pricing import (
    PricingEstimateItem,
    PricingEstimateRequest,
    PricingEstimateResponse,
    PricingFormula,
    PricingMatchContext,
)


@dataclass(slots=True)
class WalletSnapshot:
    balance: int
    frozen_balance: int


class BillingService:
    DEFAULT_FORMULAS: dict[str, PricingFormula] = {
        "scene_image": PricingFormula(
            base=8,
            per_output=2,
            size_add={"s": 0, "m": 2, "l": 6, "xl": 10},
            flag_add={"upscale": 1, "inpaint": 2},
            model_coef={"default": 1.0, "openai:gpt-image-1": 1.0},
        ),
        "video_scene": PricingFormula(
            base=6,
            per_output=2,
            size_add={"s": 0, "m": 2, "l": 3, "xl": 6},
            flag_add={"video": 8},
            model_coef={"default": 1.0, "openai:sora-2": 1.0},
        ),
    }

    @staticmethod
    def calculate_credits(formula: PricingFormula, context: PricingMatchContext) -> int:
        return formula.compute(
            count=context.count,
            size=context.size,
            flags=context.flags,
            model_key=context.model_key,
        )

    @classmethod
    def estimate_request(cls, request: PricingEstimateRequest) -> PricingEstimateResponse:
        total = 0
        items: list[PricingEstimateItem] = []
        for item in request.items:
            formula = cls.DEFAULT_FORMULAS.get(item.category, cls.DEFAULT_FORMULAS["scene_image"])
            credits = cls.calculate_credits(
                formula=formula,
                context=PricingMatchContext.model_validate(item.model_dump()),
            )
            total += credits
            items.append(PricingEstimateItem(category=item.category, credits=credits, formula=formula))
        return PricingEstimateResponse(total_credits=total, items=items)

    @staticmethod
    async def get_or_create_wallet(session: AsyncSession, workspace_id: str) -> CreditWallet:
        result = await session.execute(select(CreditWallet).where(CreditWallet.workspace_id == workspace_id))
        wallet = result.scalar_one_or_none()
        if wallet is None:
            wallet = CreditWallet(workspace_id=workspace_id, balance=0, frozen_balance=0)
            session.add(wallet)
            await session.flush()
        return wallet

    @classmethod
    async def add_credits(
        cls,
        session: AsyncSession,
        *,
        workspace_id: str,
        amount: int,
        ledger_type: str,
        user_id: str | None,
        related_entity_type: str,
        related_entity_id: str,
        note: str,
        idempotency_key: str | None = None,
    ) -> WalletSnapshot:
        wallet = await cls.get_or_create_wallet(session, workspace_id)
        wallet.balance += amount
        session.add(
            CreditLedger(
                workspace_id=workspace_id,
                user_id=user_id,
                type=ledger_type,
                amount=amount,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                note=note,
                idempotency_key=idempotency_key,
            )
        )
        await session.flush()
        return WalletSnapshot(balance=wallet.balance, frozen_balance=wallet.frozen_balance)

    @classmethod
    async def hold_credits(
        cls,
        session: AsyncSession,
        *,
        workspace_id: str,
        amount: int,
        user_id: str,
        related_entity_id: str,
    ) -> WalletSnapshot:
        wallet = await cls.get_or_create_wallet(session, workspace_id)
        if wallet.balance < amount:
            raise ValueError("积分不足")
        wallet.balance -= amount
        wallet.frozen_balance += amount
        session.add(
            CreditLedger(
                workspace_id=workspace_id,
                user_id=user_id,
                type="hold",
                amount=amount,
                related_entity_type="job",
                related_entity_id=related_entity_id,
                note="任务冻结",
                idempotency_key=f"hold:{related_entity_id}",
            )
        )
        await session.flush()
        return WalletSnapshot(balance=wallet.balance, frozen_balance=wallet.frozen_balance)

    @classmethod
    async def create_recharge_batch(
        cls,
        session: AsyncSession,
        *,
        name: str,
        credits_amount: int,
        total_count: int,
        created_by: str,
    ) -> tuple[RechargeCardBatch, list[RechargeCard]]:
        batch = RechargeCardBatch(
            name=name,
            credits_amount=credits_amount,
            total_count=total_count,
            issued_count=total_count,
            created_by=created_by,
        )
        session.add(batch)
        await session.flush()
        cards = [
            RechargeCard(
                batch_id=batch.id,
                card_code=token_hex(8).upper(),
                credits_amount=credits_amount,
            )
            for _ in range(total_count)
        ]
        session.add_all(cards)
        await session.flush()
        return batch, cards

    @classmethod
    async def redeem_card(
        cls,
        session: AsyncSession,
        *,
        workspace_id: str,
        card_code: str,
        user_id: str,
    ) -> tuple[WalletSnapshot, RechargeCard]:
        result = await session.execute(select(RechargeCard).where(RechargeCard.card_code == card_code))
        card = result.scalar_one_or_none()
        if card is None:
            raise ValueError("充值卡不存在")
        if card.status != "unused":
            raise ValueError("充值卡不可用")

        card.status = "redeemed"
        card.issued_to_workspace_id = workspace_id
        session.add(RechargeRedemption(recharge_card_id=card.id, workspace_id=workspace_id, redeemed_by=user_id))
        wallet = await cls.add_credits(
            session,
            workspace_id=workspace_id,
            amount=card.credits_amount,
            ledger_type="redeem",
            user_id=user_id,
            related_entity_type="recharge_card",
            related_entity_id=card.id,
            note="充值卡兑换",
            idempotency_key=f"redeem:{card.id}",
        )
        return wallet, card

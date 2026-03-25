from pydantic import BaseModel, Field


class WalletResponse(BaseModel):
    balance: int
    frozen_balance: int


class RechargeCardBatchCreateRequest(BaseModel):
    name: str
    credits_amount: int = Field(gt=0)
    total_count: int = Field(gt=0, le=100)


class RechargeCardResponse(BaseModel):
    id: str
    card_code: str
    credits_amount: int
    status: str


class RechargeCardBatchResponse(BaseModel):
    id: str
    name: str
    credits_amount: int
    total_count: int
    cards: list[RechargeCardResponse]


class RechargeRedeemRequest(BaseModel):
    card_code: str


class RechargeRedeemResponse(BaseModel):
    wallet: WalletResponse
    card_status: str

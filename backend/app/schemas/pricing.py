from math import ceil

from pydantic import BaseModel, Field


class PricingFormula(BaseModel):
    base: int
    per_output: int
    size_add: dict[str, int] = Field(default_factory=dict)
    flag_add: dict[str, int] = Field(default_factory=dict)
    model_coef: dict[str, float] = Field(default_factory=lambda: {"default": 1.0})
    rounding: str = "ceil_int"

    def compute(self, count: int, size: str, flags: list[str], model_key: str) -> int:
        subtotal = self.base + self.per_output * count
        subtotal += self.size_add.get(size, 0)
        subtotal += sum(self.flag_add.get(flag, 0) for flag in flags)
        total = subtotal * self.model_coef.get(model_key, self.model_coef.get("default", 1.0))
        return ceil(total)


class PricingMatchContext(BaseModel):
    count: int = 1
    size: str = "m"
    flags: list[str] = Field(default_factory=list)
    model_key: str = "default"


class PricingItemRequest(BaseModel):
    category: str
    count: int = Field(gt=0, default=1)
    size: str = "m"
    flags: list[str] = Field(default_factory=list)
    model_key: str = "default"


class PricingEstimateRequest(BaseModel):
    platform: str
    items: list[PricingItemRequest]


class PricingEstimateItem(BaseModel):
    category: str
    credits: int
    formula: PricingFormula


class PricingEstimateResponse(BaseModel):
    total_credits: int
    items: list[PricingEstimateItem]

from pydantic import BaseModel, Field


class JobItemCreateRequest(BaseModel):
    category: str
    count: int = Field(gt=0, default=1)
    size: str = "m"
    flags: list[str] = Field(default_factory=list)
    model_key: str = "default"
    prompt_draft_id: str | None = None


class JobCreateRequest(BaseModel):
    product_id: str
    platform: str
    items: list[JobItemCreateRequest]


class JobResponse(BaseModel):
    id: str
    status: str
    credits_estimated: int
    credits_frozen: int

from pydantic import BaseModel, Field


class PromptCompileRequest(BaseModel):
    product_id: str
    platform: str
    category: str
    controls: dict = Field(default_factory=dict)


class PromptDraftResponse(BaseModel):
    id: str
    platform: str
    category: str
    draft: dict

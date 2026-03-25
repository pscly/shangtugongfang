from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    product_type: str
    notes: str | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    product_type: str
    notes: str | None
    status: str

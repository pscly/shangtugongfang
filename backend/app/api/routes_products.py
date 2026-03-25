from fastapi import APIRouter

from app.api.deps import CurrentUserDep, CurrentWorkspaceDep, SessionDep
from app.models.product import Product
from app.schemas.common import APIResponse
from app.schemas.product import ProductCreateRequest, ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("", response_model=APIResponse[ProductResponse])
async def create_product(
    payload: ProductCreateRequest,
    session: SessionDep,
    workspace: CurrentWorkspaceDep,
    _: CurrentUserDep,
):
    product = Product(
        workspace_id=workspace.id,
        name=payload.name,
        product_type=payload.product_type,
        notes=payload.notes,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return APIResponse(
        data=ProductResponse(
            id=product.id,
            name=product.name,
            product_type=product.product_type,
            notes=product.notes,
            status=product.status,
        )
    )

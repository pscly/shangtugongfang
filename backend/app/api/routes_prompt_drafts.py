from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUserDep, CurrentWorkspaceDep, SessionDep
from app.models.product import Product
from app.models.prompt import PromptDraft
from app.schemas.common import APIResponse
from app.schemas.prompt import PromptCompileRequest, PromptDraftResponse

router = APIRouter(prefix="/api/prompt-drafts", tags=["prompt-drafts"])


@router.post("/compile", response_model=APIResponse[PromptDraftResponse])
async def compile_prompt_draft(
    payload: PromptCompileRequest,
    session: SessionDep,
    workspace: CurrentWorkspaceDep,
    user: CurrentUserDep,
):
    result = await session.execute(
        select(Product).where(Product.id == payload.product_id, Product.workspace_id == workspace.id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    draft = {
        "title": f"{product.name} {payload.platform} {payload.category}",
        "facts": {"product_type": product.product_type, "notes": product.notes},
        "controls": payload.controls,
        "prompt": f"请围绕{product.name}生成适合{payload.platform}的{payload.category}内容。",
    }
    prompt_draft = PromptDraft(
        workspace_id=workspace.id,
        product_id=product.id,
        platform=payload.platform,
        category=payload.category,
        draft=draft,
        created_by=user.id,
    )
    session.add(prompt_draft)
    await session.commit()
    await session.refresh(prompt_draft)
    return APIResponse(
        data=PromptDraftResponse(
            id=prompt_draft.id,
            platform=prompt_draft.platform,
            category=prompt_draft.category,
            draft=prompt_draft.draft,
        )
    )

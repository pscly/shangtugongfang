from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_admin import router as admin_router
from app.api.routes_auth import router as auth_router
from app.api.routes_credits import router as credits_router
from app.api.routes_health import router as health_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_pricing import router as pricing_router
from app.api.routes_products import router as products_router
from app.api.routes_prompt_drafts import router as prompt_drafts_router
from app.api.routes_system import router as system_router
from app.core.config import get_settings
from app.models import (  # noqa: F401
    AuditLog,
    CreditLedger,
    CreditWallet,
    Job,
    JobItem,
    Membership,
    Product,
    PromptDraft,
    RechargeCard,
    RechargeCardBatch,
    RechargeRedemption,
    User,
    Workspace,
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(credits_router)
    app.include_router(products_router)
    app.include_router(prompt_drafts_router)
    app.include_router(pricing_router)
    app.include_router(jobs_router)
    app.include_router(system_router)
    return app


app = create_app()

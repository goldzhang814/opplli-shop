from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.core.redis import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await get_redis()   # warm up Redis connection
    # Create local media dir if needed
    os.makedirs(settings.MEDIA_LOCAL_PATH, exist_ok=True)
    yield
    # Shutdown (nothing to clean up for now)


app = FastAPI(
    title="E-Commerce API",
    version="1.0.0",
    docs_url="/api/docs"      if not settings.is_production else None,
    redoc_url="/api/redoc"    if not settings.is_production else None,
    openapi_url="/api/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static media (local storage) ─────────────────────────────────────────────
if settings.STORAGE_BACKEND == "local":
    import os
    os.makedirs(settings.MEDIA_LOCAL_PATH, exist_ok=True)
    app.mount(
        settings.MEDIA_URL_PREFIX,
        StaticFiles(directory=settings.MEDIA_LOCAL_PATH),
        name="media",
    )

# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers import auth, products, cart, orders, content
from app.routers.admin import auth as admin_auth
from app.routers.admin import products as admin_products
from app.routers.admin import shipping as admin_shipping
from app.routers.admin import orders as admin_orders
from app.routers.admin import content as admin_content

app.include_router(auth.router,           prefix="/api/v1")
app.include_router(products.router,       prefix="/api/v1")
app.include_router(cart.router,           prefix="/api/v1")
app.include_router(orders.router,         prefix="/api/v1")
app.include_router(content.router,        prefix="/api/v1")
app.include_router(admin_auth.router,     prefix="/api/v1")
app.include_router(admin_products.router, prefix="/api/v1")
app.include_router(admin_shipping.router, prefix="/api/v1")
app.include_router(admin_orders.router,   prefix="/api/v1")
app.include_router(admin_content.router,  prefix="/api/v1")


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}

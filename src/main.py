import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.balance.router import router as balance_router
from src.core.enums import ApiTags
from src.order.router import router as order_router
from src.public.router import router as public_router
from src.admin.router import router as admin_router

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(public_router, prefix="/public", tags=[ApiTags.PUBLIC])
v1_router.include_router(balance_router, tags=[ApiTags.BALANCE])
v1_router.include_router(order_router, tags=[ApiTags.ORDER])
v1_router.include_router(admin_router, prefix="/admin", tags=[ApiTags.ADMIN])

app.include_router(v1_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
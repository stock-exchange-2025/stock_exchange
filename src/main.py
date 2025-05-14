import uvicorn

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from middlewares import auth_user, catch_exception
from src.admin.router import router as admin_router
from src.balance.router import router as balance_router
from src.instrument.router import router as instrument_router
from src.order.router import router as order_router
from src.transaction.router import router as transaction_router
from src.user.router import router as user_router

app = FastAPI(debug=True)

app.middleware("http")(auth_user)
app.middleware("http")(catch_exception)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],)

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(admin_router)
v1_router.include_router(balance_router)
v1_router.include_router(instrument_router)
v1_router.include_router(order_router)
v1_router.include_router(transaction_router)
v1_router.include_router(user_router)

app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
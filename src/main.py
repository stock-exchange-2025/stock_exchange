import logging

import uvicorn
from fastapi import FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.balance.router import router as balance_router
from src.core.database import engine
from src.instrument.router import router as instrument_router
from src.order.router import router as order_router
from src.transaction.router import router as transaction_router
from src.user.router import router as user_router

log = logging.getLogger(__name__)

app = FastAPI(debug=True)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> JSONResponse:
        try:
            response = await call_next(request)
        except ValidationError as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": e.errors()}
            )
        except ValueError as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": [{
                        "msg": str(e),
                        "loc": ["Unknown"],
                        "type": "value_error"
                    }]
                },
            )
        except Exception as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": [{
                        "msg": "An unexpected service error occurred",
                        "loc": ["Unknown"],
                        "type": "server_error"
                    }]
                },
            )

        return response


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        SessionLocal = Session(bind=engine)
        try:
            request.state.db = SessionLocal
            response = await call_next(request)
        finally:
            SessionLocal.close()
        return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ExceptionMiddleware)
app.add_middleware(DBSessionMiddleware)

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(balance_router)
v1_router.include_router(instrument_router)
v1_router.include_router(order_router)
v1_router.include_router(transaction_router)
v1_router.include_router(user_router)


app.include_router(v1_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
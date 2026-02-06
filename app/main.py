from logging import getLogger

from fastapi import FastAPI
from starlette.responses import JSONResponse

import app.ledger.models
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.ledger.controllers.ledger import router as ledger_router

logger = getLogger(__name__)
setup_logging()

app = FastAPI(title="Ledger MVP")
app.add_middleware(RequestContextMiddleware)
app.include_router(ledger_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception(
        "unhandled_exception",
        extra={
            "request_id": request.state.request_id,
            "impact": "unknown",
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)

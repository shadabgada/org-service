import os
from fastapi import FastAPI
from app.core.timing import TimingMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db

app = FastAPI(
    title="Org Chart Service API",
    description="API for managing organizational charts and employee hierarchies",
    version="1.0.0",
    openapi_url=f"/api/v1/openapi.json"
)
app.add_middleware(TimingMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(api_router, prefix=settings.API_PREFIX)


# This makes the app object available for Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
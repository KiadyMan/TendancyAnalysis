from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.mongodb import init_db
from backend.routes import trend_route, prediction_route, opportunity_route, pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="TendancyAnalysis API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre à l'URL de ton frontend en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trend_route.router)
app.include_router(prediction_route.router)
app.include_router(opportunity_route.router)
app.include_router(pipeline.router)


@app.get("/health")
def health():
    return {"status": "ok"}
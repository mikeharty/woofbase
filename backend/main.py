import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dogs.retriever import DogRetriever
from api.router import include_routers
from common.env import get_env


@asynccontextmanager
async def lifespan(app: FastAPI):
    initial_sync = asyncio.create_task(DogRetriever.sync_dogs())
    periodic_sync = asyncio.create_task(doggo_sync())
    yield
    initial_sync.cancel()
    periodic_sync.cancel()


async def doggo_sync():
    while True:
        await asyncio.sleep(get_env("DOG_SYNC_INTERVAL", 300))
        await DogRetriever.sync_dogs()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
include_routers(app)

from .dogs.router import router as dogs_router


def include_routers(app):
    app.include_router(dogs_router, tags=["dogs"])

from typing import Any
import asyncio

import uvicorn
from fastapi import FastAPI

from app.api.routes.api import api_router
from app.common.config import get_config
from app.common.tasks import rocketry


CONFIG = get_config()


class Server(uvicorn.Server):
    def handle_exit(self, sig: int, frame: Any | None) -> None:
        rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


def get_app() -> FastAPI:
    app = FastAPI(
        title=CONFIG.api.title,
        description=CONFIG.api.description,
        debug=CONFIG.api.debug
    )

    app.include_router(
        api_router, prefix=CONFIG.api.api_v1
    )

    return app


async def main() -> None:
    server = Server(
        config=uvicorn.Config(
            get_app(),
            port=8989,
            workers=1,
            loop='asyncio',
            reload=True
        )
    )
    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(rocketry.serve())
    await asyncio.wait([sched, api])


if __name__ == '__main__':
    asyncio.run(main())

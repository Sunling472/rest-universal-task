from fastapi import APIRouter

from app.api.routes.v1 import (
    users, token, me, register, projects,
    tasks
)


api_router = APIRouter()
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(token.router, prefix='/token', tags=['token'])
api_router.include_router(me.router, prefix='/me', tags=['me'])
api_router.include_router(register.router, prefix='/register', tags=['register'])
api_router.include_router(projects.router, prefix='/projects', tags=['projects'])
api_router.include_router(tasks.router, prefix='/tasks', tags=['tasks'])


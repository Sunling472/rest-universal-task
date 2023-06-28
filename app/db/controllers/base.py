from logging import getLogger
from abc import abstractmethod
from typing import Generic, TypeVar, Any, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_

from fastapi.exceptions import HTTPException
from fastapi import status

from app.db.schemas.base import BaseSchema, BaseSchemaOut
from app.common.errors import ErrorTexts


IN_SCHEMA = TypeVar('IN_SCHEMA', bound=BaseSchema)
OUT_SCHEMA = TypeVar('OUT_SCHEMA', bound=BaseSchemaOut)
DB_MODEL = TypeVar('DB_MODEL')


LOG = getLogger(__name__)


class BaseController(Generic[IN_SCHEMA, OUT_SCHEMA, DB_MODEL]):
    def __init__(self, session: AsyncSession, token: str | None = None) -> None:
        self.session = session
        self.token = token

    @property
    @abstractmethod
    def _create_schema(self) -> type[IN_SCHEMA]:
        ...

    @property
    @abstractmethod
    def _edit_schema(self) -> type[IN_SCHEMA]:
        ...

    @property
    @abstractmethod
    def _db_schema(self) -> type[OUT_SCHEMA]:
        ...

    @property
    @abstractmethod
    def _model(self) -> type[DB_MODEL]:
        ...

    @staticmethod
    def _raise_not_allowed() -> None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            ErrorTexts.not_allowed_error
        )

    async def list(self, model: type[DB_MODEL] | None = None,
                   db_schema: type[OUT_SCHEMA] | None = None,
                   include_deleted: bool = False,
                   start_date: int | None = None,
                   end_date: int | None = None,
                   **kw) -> list[OUT_SCHEMA]:

        if model is not None:
            query = select(model)
            if include_deleted is False:
                query = query.filter(
                    model.deleted_at == 0
                )
        else:
            query = select(self._model)
            if include_deleted is False:
                query = query.filter(
                    self._model.deleted_at == 0
                )
        if kw:
            query = query.filter_by(**kw)
        if start_date and end_date:
            query = query.filter(
                and_(
                    self._model.creater_at >= start_date,
                    self._model.created_at <= end_date
                )
            )
        elif start_date and not end_date:
            query = query.filter(
                and_(
                    self._model.created_at >= start_date
                )
            )
        elif not start_date and end_date:
            query = query.filter(
                and_(
                    self._model.created_at <= end_date
                )
            )
        items = await self.session.execute(query)
        result: list[OUT_SCHEMA] = []
        for item in items.scalars():
            result.append(
                db_schema.from_orm(item)
                if db_schema is not None
                else self._db_schema.from_orm(item)
            )

        return result

    async def prepare_list(
            self,
            items: List[DB_MODEL],
            db_schema: type[OUT_SCHEMA] | None = None) -> List[OUT_SCHEMA]:
        if db_schema is None:
            db_schema = self._db_schema
        result: List[OUT_SCHEMA] = []
        for item in items:
            result.append(db_schema.from_orm(item))
        return result

    async def get(self, item_id: str, from_orm: bool = True,
                  model: type[DB_MODEL] | None = None,
                  db_schema: type[OUT_SCHEMA] | None = None) -> DB_MODEL | OUT_SCHEMA:
        if model is not None:
            query = select(model).filter(
                model.deleted_at == 0,
                model.id == item_id
            )
        else:
            query = select(self._model).filter(
                self._model.deleted_at == 0,
                self._model.id == item_id
            )
        item = await self.session.execute(query)
        item = item.scalars().one_or_none()
        if not item:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorTexts.model_not_exist_error.format(
                    model_name=self._model.__name__,
                    item_id=item_id
                )
            )
        if from_orm is True:
            if db_schema is not None:
                return db_schema.from_orm(item)
            else:
                return self._db_schema.from_orm(item)
        return item

    async def create(self, create_schema: IN_SCHEMA | None = None,
                     from_orm: bool = True,
                     model: type[DB_MODEL] | None = None,
                     db_schema: type[IN_SCHEMA] | None = None, **kwargs) -> DB_MODEL | OUT_SCHEMA:
        result: dict[str, Any] = {}
        for k, v in create_schema.dict().items() if create_schema else kwargs.items():
            if v is not None:
                result[k] = v
        if model is not None:
            item = model(**result)
        else:
            item = self._model(**result)
        try:
            self.session.add(item)
            await self.session.commit()
        except IntegrityError as ex:
            await self.session.rollback()
            LOG.exception(ex)
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                ErrorTexts.database_error.format(
                    details=ex.orig
                )
            )
        if from_orm:
            if db_schema is not None:
                return db_schema.from_orm(item)
            else:
                return self._db_schema.from_orm(item)
        return item

    async def edit(self, item_id: str,
                   edit_schema: IN_SCHEMA | None = None,
                   model: type[DB_MODEL] | None = None,
                   db_schema: type[OUT_SCHEMA] | None = None, **kwargs) -> OUT_SCHEMA:
        result: dict[str, Any] = {}
        if model is not None:
            item = await self.session.get(model, item_id)
        else:
            item = await self.session.get(self._model, item_id)
        if (edit_schema and not kwargs) or (
                not edit_schema and kwargs):
            self.session.expunge(item)

            for k, v in edit_schema.dict().items() if edit_schema else kwargs.items():
                if v is not None:
                    result[k] = v

            for k, v in result.items():
                setattr(item, k, v)
            try:
                self.session.add(item)
                await self.session.commit()
            except IntegrityError as ex:
                await self.session.rollback()
                raise HTTPException(
                    status.HTTP_502_BAD_GATEWAY,
                    ErrorTexts.database_error.format(
                        details=ex.detail
                    )
                )
            if db_schema is not None:
                return db_schema.from_orm(item)
            else:
                return self._db_schema.from_orm(item)
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorTexts.database_not_params_error
            )

    async def delete(self, item_id: str,
                     model: type[DB_MODEL] | None = None,
                     db_schema: type[OUT_SCHEMA] | None = None) -> None:
        await self.edit(
            item_id,
            model=model,
            db_schema=db_schema,
            deleted_at=int(datetime.utcnow().timestamp())
        )

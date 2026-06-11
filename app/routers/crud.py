import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session


def orm_kwargs(payload: BaseModel, partial: bool = False) -> dict:
    data = payload.model_dump(exclude_unset=partial)
    if "metadata" in data:
        data["meta"] = data.pop("metadata")
    return data


async def get_or_404(session: AsyncSession, model, item_id: uuid.UUID):
    obj = await session.get(model, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


def crud_router(
    *,
    prefix: str,
    tag: str,
    model,
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    before_save: Callable | None = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", response_model=list[read_schema])
    async def list_items(session: AsyncSession = Depends(get_session)):
        result = await session.scalars(select(model).order_by(model.created_at))
        return list(result)

    @router.post("", response_model=read_schema, status_code=201)
    async def create_item(payload: create_schema, session: AsyncSession = Depends(get_session)):
        obj = model(**orm_kwargs(payload))
        if before_save:
            before_save(obj)
        session.add(obj)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409, detail="conflicts with an existing record")
        await session.refresh(obj)
        return obj

    @router.get("/{item_id}", response_model=read_schema)
    async def get_item(item_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
        return await get_or_404(session, model, item_id)

    @router.put("/{item_id}", response_model=read_schema)
    async def update_item(
        item_id: uuid.UUID,
        payload: update_schema,
        session: AsyncSession = Depends(get_session),
    ):
        obj = await get_or_404(session, model, item_id)
        for key, value in orm_kwargs(payload, partial=True).items():
            setattr(obj, key, value)
        if before_save:
            before_save(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    @router.delete("/{item_id}", status_code=204)
    async def delete_item(item_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
        obj = await get_or_404(session, model, item_id)
        await session.delete(obj)
        await session.commit()

    return router

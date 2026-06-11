import uuid
from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db import get_session
from app.export.cyclonedx import to_cyclonedx
from app.export.markdown import to_markdown
from app.export.native import build_aibom
from app.registry import COMPONENTS
from app.routers.crud import crud_router, get_or_404, orm_kwargs

router = crud_router(
    prefix="/applications",
    tag="applications",
    model=models.Application,
    create_schema=schemas.ApplicationCreate,
    update_schema=schemas.ApplicationUpdate,
    read_schema=schemas.ApplicationRead,
)


@router.get("/{item_id}/links", response_model=list[schemas.LinkRead])
async def list_links(item_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await get_or_404(session, models.Application, item_id)
    result = await session.scalars(
        select(models.AppLink).where(models.AppLink.app_id == item_id)
    )
    return list(result)


@router.post("/{item_id}/links", response_model=schemas.LinkRead, status_code=201)
async def create_link(
    item_id: uuid.UUID,
    payload: schemas.LinkCreate,
    session: AsyncSession = Depends(get_session),
):
    await get_or_404(session, models.Application, item_id)
    component_model, _ = COMPONENTS[payload.component_type]
    component = await session.get(component_model, payload.component_id)
    if component is None:
        raise HTTPException(status_code=404, detail=f"{payload.component_type} not found")
    link = models.AppLink(app_id=item_id, **orm_kwargs(payload))
    session.add(link)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="component already linked")
    await session.refresh(link)
    return link


@router.delete("/{item_id}/links/{link_id}", status_code=204)
async def delete_link(
    item_id: uuid.UUID, link_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    link = await get_or_404(session, models.AppLink, link_id)
    if link.app_id != item_id:
        raise HTTPException(status_code=404, detail="AppLink not found")
    await session.delete(link)
    await session.commit()


@router.get("/{item_id}/aibom")
async def export_aibom(
    item_id: uuid.UUID,
    format: Literal["native", "cyclonedx"] = "native",
    session: AsyncSession = Depends(get_session),
):
    app = await get_or_404(session, models.Application, item_id)
    aibom = await build_aibom(session, app)
    if format == "cyclonedx":
        return to_cyclonedx(aibom)
    return aibom


@router.get("/{item_id}/report.md", response_class=PlainTextResponse)
async def export_report(item_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    app = await get_or_404(session, models.Application, item_id)
    aibom = await build_aibom(session, app)
    return PlainTextResponse(to_markdown(aibom), media_type="text/markdown")

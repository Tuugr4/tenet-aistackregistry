from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Application, AppLink
from app.registry import COMPONENTS
from app.schemas import ApplicationRead


async def build_aibom(session: AsyncSession, app: Application) -> dict:
    links = await session.scalars(select(AppLink).where(AppLink.app_id == app.id))
    components: dict[str, list] = {key: [] for key in COMPONENTS}
    for link in links:
        model, read_schema = COMPONENTS[link.component_type]
        obj = await session.get(model, link.component_id)
        if obj is None:
            continue
        entry = read_schema.model_validate(obj).model_dump(mode="json")
        entry["role"] = link.role
        components[link.component_type].append(entry)
    return {
        "aibom_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "application": ApplicationRead.model_validate(app).model_dump(mode="json"),
        "components": components,
    }

import uuid
from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class CreateBase(BaseModel):
    metadata: dict = Field(default_factory=dict)


class UpdateBase(BaseModel):
    metadata: dict | None = None


class ReadBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(
        default_factory=dict, validation_alias=AliasChoices("meta", "metadata")
    )

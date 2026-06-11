import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JsonCol, RecordMixin


class Application(RecordMixin, Base):
    __tablename__ = "applications"

    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None] = mapped_column(String(200))
    environment: Mapped[str] = mapped_column(String(20), default="dev")


class Provider(RecordMixin, Base):
    __tablename__ = "providers"

    name: Mapped[str] = mapped_column(String(200), unique=True)
    kind: Mapped[str] = mapped_column(String(20), default="api")
    base_url: Mapped[str | None] = mapped_column(String(500))


class MLModel(RecordMixin, Base):
    __tablename__ = "models"

    provider_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("providers.id"))
    name: Mapped[str] = mapped_column(String(200))
    model_id: Mapped[str] = mapped_column(String(200))
    family: Mapped[str | None] = mapped_column(String(100))
    modality: Mapped[str] = mapped_column(String(50), default="text")
    context_window: Mapped[int | None] = mapped_column(Integer)
    license: Mapped[str | None] = mapped_column(String(100))


class Prompt(RecordMixin, Base):
    __tablename__ = "prompts"
    __table_args__ = (UniqueConstraint("name", "version"),)

    name: Mapped[str] = mapped_column(String(200))
    version: Mapped[str] = mapped_column(String(50))
    template: Mapped[str] = mapped_column(Text)
    variables: Mapped[list] = mapped_column(JsonCol, default=list)
    hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="draft")


class Dataset(RecordMixin, Base):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(String(200))
    version: Mapped[str | None] = mapped_column(String(50))
    source_url: Mapped[str | None] = mapped_column(String(500))
    license: Mapped[str | None] = mapped_column(String(100))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    hash: Mapped[str | None] = mapped_column(String(64))


class FineTune(RecordMixin, Base):
    __tablename__ = "fine_tunes"

    name: Mapped[str] = mapped_column(String(200))
    base_model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("models.id"))
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("datasets.id"))
    job_id: Mapped[str | None] = mapped_column(String(200))
    hyperparams: Mapped[dict] = mapped_column(JsonCol, default=dict)
    result_model_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("models.id"))


class EmbeddingIndex(RecordMixin, Base):
    __tablename__ = "embedding_indexes"

    name: Mapped[str] = mapped_column(String(200))
    embedding_model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("models.id"))
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("datasets.id"))
    dimension: Mapped[int] = mapped_column(Integer)
    metric: Mapped[str] = mapped_column(String(20), default="cosine")


class VectorDB(RecordMixin, Base):
    __tablename__ = "vector_dbs"

    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(50))
    endpoint: Mapped[str | None] = mapped_column(String(500))
    collection: Mapped[str | None] = mapped_column(String(200))


class EvalResult(RecordMixin, Base):
    __tablename__ = "eval_results"

    name: Mapped[str] = mapped_column(String(200))
    target_type: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    metrics: Mapped[dict] = mapped_column(JsonCol, default=dict)
    passed: Mapped[bool | None] = mapped_column(Boolean)
    run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AppLink(RecordMixin, Base):
    __tablename__ = "app_links"
    __table_args__ = (UniqueConstraint("app_id", "component_type", "component_id"),)

    app_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    component_type: Mapped[str] = mapped_column(String(30))
    component_id: Mapped[uuid.UUID]
    role: Mapped[str | None] = mapped_column(String(100))

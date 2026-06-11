import uuid
from datetime import datetime
from typing import Literal

from app.schemas.common import CreateBase, ReadBase, UpdateBase

Environment = Literal["dev", "staging", "prod"]
ProviderKind = Literal["api", "self_hosted"]
PromptStatus = Literal["draft", "prod", "retired"]
EvalTarget = Literal["model", "prompt"]
ComponentType = Literal[
    "provider",
    "model",
    "prompt",
    "dataset",
    "fine_tune",
    "embedding_index",
    "vector_db",
    "eval_result",
]


class ApplicationCreate(CreateBase):
    name: str
    slug: str
    description: str | None = None
    owner: str | None = None
    environment: Environment = "dev"


class ApplicationUpdate(UpdateBase):
    name: str | None = None
    description: str | None = None
    owner: str | None = None
    environment: Environment | None = None


class ApplicationRead(ReadBase):
    name: str
    slug: str
    description: str | None
    owner: str | None
    environment: Environment


class ProviderCreate(CreateBase):
    name: str
    kind: ProviderKind = "api"
    base_url: str | None = None


class ProviderUpdate(UpdateBase):
    name: str | None = None
    kind: ProviderKind | None = None
    base_url: str | None = None


class ProviderRead(ReadBase):
    name: str
    kind: ProviderKind
    base_url: str | None


class MLModelCreate(CreateBase):
    name: str
    model_id: str
    provider_id: uuid.UUID | None = None
    family: str | None = None
    modality: str = "text"
    context_window: int | None = None
    license: str | None = None


class MLModelUpdate(UpdateBase):
    name: str | None = None
    model_id: str | None = None
    provider_id: uuid.UUID | None = None
    family: str | None = None
    modality: str | None = None
    context_window: int | None = None
    license: str | None = None


class MLModelRead(ReadBase):
    name: str
    model_id: str
    provider_id: uuid.UUID | None
    family: str | None
    modality: str
    context_window: int | None
    license: str | None


class PromptCreate(CreateBase):
    name: str
    version: str
    template: str
    variables: list[str] = []
    status: PromptStatus = "draft"


class PromptUpdate(UpdateBase):
    template: str | None = None
    variables: list[str] | None = None
    status: PromptStatus | None = None


class PromptRead(ReadBase):
    name: str
    version: str
    template: str
    variables: list[str]
    hash: str
    status: PromptStatus


class DatasetCreate(CreateBase):
    name: str
    version: str | None = None
    source_url: str | None = None
    license: str | None = None
    size_bytes: int | None = None
    hash: str | None = None


class DatasetUpdate(UpdateBase):
    name: str | None = None
    version: str | None = None
    source_url: str | None = None
    license: str | None = None
    size_bytes: int | None = None
    hash: str | None = None


class DatasetRead(ReadBase):
    name: str
    version: str | None
    source_url: str | None
    license: str | None
    size_bytes: int | None
    hash: str | None


class FineTuneCreate(CreateBase):
    name: str
    base_model_id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    job_id: str | None = None
    hyperparams: dict = {}
    result_model_id: uuid.UUID | None = None


class FineTuneUpdate(UpdateBase):
    name: str | None = None
    job_id: str | None = None
    hyperparams: dict | None = None
    result_model_id: uuid.UUID | None = None


class FineTuneRead(ReadBase):
    name: str
    base_model_id: uuid.UUID
    dataset_id: uuid.UUID | None
    job_id: str | None
    hyperparams: dict
    result_model_id: uuid.UUID | None


class EmbeddingIndexCreate(CreateBase):
    name: str
    embedding_model_id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    dimension: int
    metric: str = "cosine"


class EmbeddingIndexUpdate(UpdateBase):
    name: str | None = None
    dataset_id: uuid.UUID | None = None
    dimension: int | None = None
    metric: str | None = None


class EmbeddingIndexRead(ReadBase):
    name: str
    embedding_model_id: uuid.UUID
    dataset_id: uuid.UUID | None
    dimension: int
    metric: str


class VectorDBCreate(CreateBase):
    name: str
    kind: str
    endpoint: str | None = None
    collection: str | None = None


class VectorDBUpdate(UpdateBase):
    name: str | None = None
    kind: str | None = None
    endpoint: str | None = None
    collection: str | None = None


class VectorDBRead(ReadBase):
    name: str
    kind: str
    endpoint: str | None
    collection: str | None


class EvalResultCreate(CreateBase):
    name: str
    target_type: EvalTarget
    target_id: uuid.UUID
    metrics: dict = {}
    passed: bool | None = None
    run_at: datetime | None = None


class EvalResultUpdate(UpdateBase):
    metrics: dict | None = None
    passed: bool | None = None
    run_at: datetime | None = None


class EvalResultRead(ReadBase):
    name: str
    target_type: EvalTarget
    target_id: uuid.UUID
    metrics: dict
    passed: bool | None
    run_at: datetime | None


class LinkCreate(CreateBase):
    component_type: ComponentType
    component_id: uuid.UUID
    role: str | None = None


class LinkRead(ReadBase):
    app_id: uuid.UUID
    component_type: ComponentType
    component_id: uuid.UUID
    role: str | None

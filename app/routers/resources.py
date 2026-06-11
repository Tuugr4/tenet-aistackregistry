import hashlib

from app import models, schemas
from app.routers.crud import crud_router


def set_prompt_hash(prompt: models.Prompt) -> None:
    prompt.hash = hashlib.sha256(prompt.template.encode()).hexdigest()


resource_routers = [
    crud_router(
        prefix="/providers",
        tag="providers",
        model=models.Provider,
        create_schema=schemas.ProviderCreate,
        update_schema=schemas.ProviderUpdate,
        read_schema=schemas.ProviderRead,
    ),
    crud_router(
        prefix="/models",
        tag="models",
        model=models.MLModel,
        create_schema=schemas.MLModelCreate,
        update_schema=schemas.MLModelUpdate,
        read_schema=schemas.MLModelRead,
    ),
    crud_router(
        prefix="/prompts",
        tag="prompts",
        model=models.Prompt,
        create_schema=schemas.PromptCreate,
        update_schema=schemas.PromptUpdate,
        read_schema=schemas.PromptRead,
        before_save=set_prompt_hash,
    ),
    crud_router(
        prefix="/datasets",
        tag="datasets",
        model=models.Dataset,
        create_schema=schemas.DatasetCreate,
        update_schema=schemas.DatasetUpdate,
        read_schema=schemas.DatasetRead,
    ),
    crud_router(
        prefix="/fine-tunes",
        tag="fine-tunes",
        model=models.FineTune,
        create_schema=schemas.FineTuneCreate,
        update_schema=schemas.FineTuneUpdate,
        read_schema=schemas.FineTuneRead,
    ),
    crud_router(
        prefix="/embedding-indexes",
        tag="embedding-indexes",
        model=models.EmbeddingIndex,
        create_schema=schemas.EmbeddingIndexCreate,
        update_schema=schemas.EmbeddingIndexUpdate,
        read_schema=schemas.EmbeddingIndexRead,
    ),
    crud_router(
        prefix="/vector-dbs",
        tag="vector-dbs",
        model=models.VectorDB,
        create_schema=schemas.VectorDBCreate,
        update_schema=schemas.VectorDBUpdate,
        read_schema=schemas.VectorDBRead,
    ),
    crud_router(
        prefix="/eval-results",
        tag="eval-results",
        model=models.EvalResult,
        create_schema=schemas.EvalResultCreate,
        update_schema=schemas.EvalResultUpdate,
        read_schema=schemas.EvalResultRead,
    ),
]

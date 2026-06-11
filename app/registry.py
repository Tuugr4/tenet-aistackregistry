from app import models, schemas

COMPONENTS = {
    "provider": (models.Provider, schemas.ProviderRead),
    "model": (models.MLModel, schemas.MLModelRead),
    "prompt": (models.Prompt, schemas.PromptRead),
    "dataset": (models.Dataset, schemas.DatasetRead),
    "fine_tune": (models.FineTune, schemas.FineTuneRead),
    "embedding_index": (models.EmbeddingIndex, schemas.EmbeddingIndexRead),
    "vector_db": (models.VectorDB, schemas.VectorDBRead),
    "eval_result": (models.EvalResult, schemas.EvalResultRead),
}

"""LLM and embedding models factories"""

from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


@lru_cache
def get_chat_model(model: str | None = None) -> BaseChatModel:
    return init_chat_model(
        model or settings.chat_model,
        model_provider="openai",
        api_key=settings.openai_api_key.get_secret_value(),
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )


@lru_cache
def get_embeddings() -> Embeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key.get_secret_value(),
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )

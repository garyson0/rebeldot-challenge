import openai
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


class ServiceUnavailableError(Exception):
    """OpenAI or the database could not be reached; the API answers with 503."""


# OpenAI: timeout, connection error, rate limit, wrong API key
# LangChain/Pydantic: unexpected format
LLM_ERRORS = (openai.APIError, OutputParserException, ValidationError)

DATABASE_ERRORS = (SQLAlchemyError,)

# FAQ search errors
SEARCH_ERRORS = LLM_ERRORS + DATABASE_ERRORS

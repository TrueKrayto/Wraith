import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def get_llm_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")

    if not api_key:
        raise ValueError("LLM_API_KEY is not configured.")

    client_kwargs = {
        "api_key": api_key,
    }

    if base_url:
        client_kwargs["base_url"] = base_url

    return OpenAI(**client_kwargs)


def get_llm_model() -> str:
    model = os.getenv("LLM_MODEL")

    if not model:
        raise ValueError("LLM_MODEL is not configured.")

    return model
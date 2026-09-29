import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_chat_completion(messages, model, max_tokens, temperature):
    """Send a request to the OpenAI API and return the response."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        logger.info(f"OpenAI request sent for model: {model}")
        return response
    except Exception as e:
        logger.error(f"OpenAI API request failed: {e}")
        raise

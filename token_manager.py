import logging

import tiktoken

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
MAX_TOKEN = 85
TEMPERATURE = 0.5
TOKEN_BUDGET = 85
ALL_TOKEN_USED = 0
MESSAGES_STORED = 0
MESSAGES_DELETED = 0


def encoding(model):
    """Get the encoding for the chosen model."""
    try:
        return tiktoken.encoding_for_model(model)
    except Exception as e:
        logger.error(f"Encoding load failed for {model}: {e}")
        return tiktoken.get_encoding("cl100k_base")


ENCODING = encoding(MODEL)


def count_tokens(text):
    """Encode text and return the amount of tokens in it."""
    tokens = len(ENCODING.encode(text))
    logger.info(f"Counted {tokens} tokens for text: {text[:30]}...")
    return tokens


def total_tokens(messages):
    """Count the total number of tokens in the message list."""
    global ALL_TOKEN_USED
    try:
        token_count = sum(count_tokens(msg["content"]) for msg in messages if "content" in msg)
        ALL_TOKEN_USED += token_count
        return token_count
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        return 0


def token_wrapper(messages):
    """Delete old messages when the token budget is exceeded."""
    global MESSAGES_DELETED
    try:
        while total_tokens(messages) > TOKEN_BUDGET:
            if len(messages) <= 2:
                break
            deleted = messages.pop(1)
            MESSAGES_DELETED += 1
            logger.warning(f"Deleted message to stay within token budget: {deleted}")
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")

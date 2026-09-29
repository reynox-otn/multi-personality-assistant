import logging

import token_manager
from api_client import create_chat_completion
from personalities import DEFAULT_PERSONALITY, PERSONALITIES

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = PERSONALITIES[DEFAULT_PERSONALITY]
messages = [{"role": "system", "content": SYSTEM_PROMPT}]


def reset_conversation():
    """Reset the chat, all counter and tracking variables."""
    global messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    token_manager.MESSAGES_STORED = 0
    token_manager.MESSAGES_DELETED = 0
    token_manager.ALL_TOKEN_USED = 0
    logger.info("Conversation reset and counters reseted.")
    return messages


def set_personality(choice):
    """Update the active conversation personality and reset the chat."""
    global SYSTEM_PROMPT, messages
    SYSTEM_PROMPT = PERSONALITIES[choice]
    reset_conversation()
    logger.info(f"Personality changed to: {choice}")
    return messages


def count_messages_strored():
    """Count how many assistant messages have been stored."""
    count = sum(1 for msg in messages if msg["role"] == "assistant")
    token_manager.MESSAGES_STORED = count
    logger.info(f"Stored assistant messages: {count}")
    return token_manager.MESSAGES_STORED


def get_status_summary():
    """Return the current app status summary for the GUI."""
    summary = {
        "model": token_manager.MODEL,
        "tokens": token_manager.ALL_TOKEN_USED,
        "deleted": token_manager.MESSAGES_DELETED,
    }
    logger.info(f"Status summary requested: {summary}")
    return summary


def chat_bot(user_input):
    """Send a request to the OpenAI API and return the response."""
    global messages
    logger.info(f"User input received: {user_input[:50]}...")
    messages.append({"role": "user", "content": user_input})

    try:
        response = create_chat_completion(
            messages=messages,
            model=token_manager.MODEL,
            max_tokens=token_manager.MAX_TOKEN,
            temperature=token_manager.TEMPERATURE,
        )
        reply = response.choices[0].message.content
        logger.info(f"Assistant reply generated: {reply[:50]}...")
    except Exception as e:
        logger.error(f"Chat completion request failed: {e}")
        raise

    messages.append({"role": "assistant", "content": reply})
    count_messages_strored()
    token_manager.token_wrapper(messages)

    return reply

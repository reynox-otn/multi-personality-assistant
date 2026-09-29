import unittest
from unittest.mock import patch

import backend
import token_manager


class BackendTests(unittest.TestCase):
    """Test the backend chatbot helpers and conversation state."""

    def setUp(self):
        """Reset the chat and counters before each test."""
        backend.reset_conversation()
        token_manager.MESSAGES_STORED = 0
        token_manager.MESSAGES_DELETED = 0
        token_manager.ALL_TOKEN_USED = 0

    def test_reset_conversation_resets_chat_and_counters(self):
        """Reset the conversation and restore the default system prompt."""
        backend.messages.append({"role": "user", "content": "hello"})
        backend.messages.append({"role": "assistant", "content": "hi there"})
        token_manager.MESSAGES_STORED = 1
        token_manager.MESSAGES_DELETED = 2
        token_manager.ALL_TOKEN_USED = 50

        result = backend.reset_conversation()

        self.assertEqual(result, [{"role": "system", "content": backend.SYSTEM_PROMPT}])
        self.assertEqual(backend.messages, [{"role": "system", "content": backend.SYSTEM_PROMPT}])
        self.assertEqual(token_manager.MESSAGES_STORED, 0)
        self.assertEqual(token_manager.MESSAGES_DELETED, 0)
        self.assertEqual(token_manager.ALL_TOKEN_USED, 0)

    def test_set_personality__and_resets_chat(self):
        """Change the selected personality and reset the conversation."""
        backend.set_personality("Professional 🤵")

        self.assertEqual(backend.SYSTEM_PROMPT, backend.PERSONALITIES["Professional 🤵"])
        self.assertEqual(backend.messages, [{"role": "system", "content": backend.SYSTEM_PROMPT}])

    def test_count_messages_strored_counts_assistant_messages(self):
        """Count how many assistant messages are currently stored."""
        backend.messages.extend(
            [
                {"role": "user", "content": "question"},
                {"role": "assistant", "content": "answer 1"},
                {"role": "assistant", "content": "answer 2"},
            ]
        )

        result = backend.count_messages_strored()

        self.assertEqual(result, 2)
        self.assertEqual(token_manager.MESSAGES_STORED, 2)

    def test_get_status_summary(self):
        """Return the current token and deletion counters for the GUI status."""
        token_manager.MESSAGES_DELETED = 3
        token_manager.ALL_TOKEN_USED = 120

        result = backend.get_status_summary()

        self.assertEqual(result["model"], token_manager.MODEL)
        self.assertEqual(result["tokens"], 120)
        self.assertEqual(result["deleted"], 3)

    def test_chat_bot_sends_request_and_appends_response(self):
        """Send a user message, store the response, and keep the history updated."""
        response = type(
            "Response",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {"message": type("Message", (), {"content": "This is a mocked reply."})()},
                    )()
                ]
            },
        )()

        with patch("backend.create_chat_completion", return_value=response) as mock_create:
            result = backend.chat_bot("How are you?")

        self.assertEqual(result, "This is a mocked reply.")
        self.assertEqual(backend.messages[-2], {"role": "user", "content": "How are you?"})
        self.assertEqual(backend.messages[-1], {"role": "assistant", "content": "This is a mocked reply."})
        mock_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()

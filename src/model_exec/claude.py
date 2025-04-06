from typing import List, Dict, Any

from anthropic import Anthropic

from model_exec.model_executor import Message, ModelExecutor



SONNET_3_5_MODEL_NAME = "claude-3-5-sonnet-20241022"
SONNET_3_7_MODEL_NAME = "claude-3-7-sonnet-20250219"
HAIKU_3_5_MODEL_NAME = "claude-3-5-haiku-20241022"


class ClaudeModelExecutor(ModelExecutor):
    """
    Executes requests to Claude models via the Anthropic API.
    """

    ai_model_name = None  # To be set by subclasses

    def __init__(self):
        self.client = Anthropic()

        # Ensure subclasses properly set the model name
        if self.ai_model_name is None:
            raise ValueError(f"Model name must be set in {self.__class__.__name__}")

    @staticmethod
    def _create_api_message(role: str, content: str) -> Dict[str, Any]:
        """Creates a properly formatted message for the Claude API."""
        return {"role": role, "content": [{"type": "text", "text": content}]}

    def execute(
        self,
        sys_msg: str,
        messages: List[Message],
        temperature: float = 0.2,
        stop_sequences: List[str] = None,
        max_tokens: int = 4000,
    ) -> str:
        """
        Makes an API call to Claude, handling message preprocessing and conversion.

        Args:
            sys_msg: System message providing conversation context
            messages: List of Message objects representing the conversation
            temperature: Controls response randomness (0.0-1.0)
            stop_sequences: List of strings that, if generated, will end the response
            max_tokens: Maximum tokens in the response

        Returns:
            str: Claude's response text
        """
        api_messages = []

        for msg in messages:
            api_messages.append(self._create_api_message(msg.role, msg.content))

        message = self.client.beta.messages.create(
            model=self.ai_model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=sys_msg,
            messages=api_messages,
            stop_sequences=stop_sequences,
        )

        if stop_sequences and message.stop_reason == "stop_sequence":
            return message.content[0].text + message.stop_sequence

        return message.content[0].text


class Claude35SonnetExec(ClaudeModelExecutor):
    """Executes requests specifically for Claude-3.5-Sonnet model."""

    ai_model_name = SONNET_3_5_MODEL_NAME


class Claude37SonnetExec(ClaudeModelExecutor):
    """Executes requests specifically for Claude-3.7-Sonnet model."""

    ai_model_name = SONNET_3_7_MODEL_NAME


class Claude35HaikuExec(ClaudeModelExecutor):
    """Executes requests specifically for Claude-3.5-Haiku model."""

    ai_model_name = HAIKU_3_5_MODEL_NAME

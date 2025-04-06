from abc import ABC, abstractmethod
from typing import List, Literal, TypeAlias

from pydantic import BaseModel

MSG_ROLE: TypeAlias = Literal["user", "assistant"]

class Message(BaseModel):
    role: MSG_ROLE
    content: str


class ModelExecutor(ABC):
    ai_model_name: str

    @abstractmethod
    def execute(
            self,
            sys_msg: str,
            messages: List[Message],
            temperature: float = 0.2,
            stop_sequences: List[str] = None
    ) -> str:
        pass

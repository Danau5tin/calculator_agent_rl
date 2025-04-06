from dataclasses import dataclass

@dataclass
class JudgeResponse:
    thoughts: str
    score: float

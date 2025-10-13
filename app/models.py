from pydantic import BaseModel
from typing import List, Literal
class AssistantConfig(BaseModel):
    name: str = 'Assistant'
    languages: List[Literal['ky','ru']] = ['ky','ru']
    wake_word_enabled: bool = True
class Command(BaseModel):
    id: str; title: str; payload: dict
class Macro(BaseModel):
    id: str; title: str; command_ids: List[str] = []

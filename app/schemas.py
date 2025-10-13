from pydantic import BaseModel
from typing import List
from .models import AssistantConfig, Command, Macro
class ConfigResponse(BaseModel):
    config: AssistantConfig
    commands: List[Command]
    macros: List[Macro]

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field

class ToolInterface(BaseModel, ABC):
    name: str = Field(description="The name of the tool")
    description: str = Field(description="A description of what the tool does")
    
    @abstractmethod
    async def use(self, input_text: str) -> str:
        """Use the tool with the given input text."""
        pass

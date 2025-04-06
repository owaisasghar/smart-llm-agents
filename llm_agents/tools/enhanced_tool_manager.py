from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from llm_agents.tools.base import ToolInterface
import asyncio
from datetime import datetime

class ToolStats(BaseModel):
    usage_count: int = 0
    success_count: int = 0
    error_count: int = 0
    last_used: Optional[datetime] = None
    average_response_time: float = 0.0

class EnhancedToolManager(BaseModel):
    tools: List[ToolInterface] = Field(default_factory=list)
    tool_stats: Dict[str, ToolStats] = Field(default_factory=dict)
    tool_chains: Dict[str, List[str]] = Field(default_factory=dict)

    def __init__(self, tools: List[ToolInterface], **data):
        super().__init__(tools=tools, **data)
        # Initialize stats for each tool
        for tool in tools:
            self.tool_stats[tool.name] = ToolStats()

    def define_tool_chain(self, name: str, tool_names: List[str]):
        """Define a sequence of tools to be executed in order."""
        self.tool_chains[name] = tool_names

    async def execute_tool_chain(self, chain_name: str, initial_input: str) -> str:
        """Execute a predefined chain of tools."""
        if chain_name not in self.tool_chains:
            raise ValueError(f"Tool chain '{chain_name}' not found")
        
        current_input = initial_input
        for tool_name in self.tool_chains[chain_name]:
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found in chain '{chain_name}'")
            
            start_time = datetime.now()
            try:
                result = await tool.use(current_input)
                self.tool_stats[tool_name].success_count += 1
            except Exception as e:
                self.tool_stats[tool_name].error_count += 1
                raise e
            finally:
                self.tool_stats[tool_name].usage_count += 1
                self.tool_stats[tool_name].last_used = datetime.now()
                response_time = (datetime.now() - start_time).total_seconds()
                self.tool_stats[tool_name].average_response_time = (
                    (self.tool_stats[tool_name].average_response_time * 
                     (self.tool_stats[tool_name].usage_count - 1) + 
                     response_time) / self.tool_stats[tool_name].usage_count
                )
            
            current_input = result
        
        return current_input

    def get_tool_stats(self) -> Dict[str, ToolStats]:
        """Get statistics for all tools."""
        return self.tool_stats

    async def execute_tool(self, tool_name: str, input_text: str) -> str:
        """Execute a single tool and update its statistics."""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        start_time = datetime.now()
        try:
            result = await tool.use(input_text)
            self.tool_stats[tool_name].success_count += 1
            return result
        except Exception as e:
            self.tool_stats[tool_name].error_count += 1
            raise e
        finally:
            self.tool_stats[tool_name].usage_count += 1
            self.tool_stats[tool_name].last_used = datetime.now()
            response_time = (datetime.now() - start_time).total_seconds()
            self.tool_stats[tool_name].average_response_time = (
                (self.tool_stats[tool_name].average_response_time * 
                 (self.tool_stats[tool_name].usage_count - 1) + 
                 response_time) / self.tool_stats[tool_name].usage_count
            )

    def get_most_used_tools(self, limit: int = 5) -> List[Dict[str, Any]]:
        sorted_stats = sorted(
            self.tool_stats.items(),
            key=lambda x: x[1].usage_count,
            reverse=True
        )
        return [
            {"tool": name, "stats": stats.dict()}
            for name, stats in sorted_stats[:limit]
        ]

    def validate_tool_input(self, tool_name: str, input_data: str) -> bool:
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        # Add input validation logic here based on tool requirements
        return True 
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Callable
from pydantic import BaseModel, Field
import asyncio
import json
import logging
from datetime import datetime
from llm_agents.tools.base import ToolInterface

class ToolError(Exception):
    def __init__(self, message: str, tool_name: str, error_type: str = "execution"):
        self.message = message
        self.tool_name = tool_name
        self.error_type = error_type
        super().__init__(f"{tool_name} error ({error_type}): {message}")

class ToolMetadata(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_parameters: List[str] = Field(default_factory=list)
    optional_parameters: List[str] = Field(default_factory=list)

class ToolResult(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AdvancedTool(ToolInterface):
    name: str = Field(default="AdvancedTool", description="Base class for advanced tools")
    description: str = "A base class for advanced tools with additional features."
    max_retries: int = 3
    timeout: int = 30
    cache_results: bool = True
    result_cache: Dict[str, str] = Field(default_factory=dict)
    pre_processors: List[Callable[[str], str]] = Field(default_factory=list)
    post_processors: List[Callable[[str], str]] = Field(default_factory=list)

    def __init__(self):
        super().__init__()
        self.metadata = self._get_metadata()
        self.logger = logging.getLogger(self.metadata.name)
        self._validate_metadata()

    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        pass

    def _validate_metadata(self):
        if not self.metadata.name:
            raise ValueError("Tool name is required")
        if not self.metadata.description:
            raise ValueError("Tool description is required")
        if not self.metadata.required_parameters:
            self.metadata.required_parameters = []

    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        pass

    async def use(self, input_text: str) -> str:
        """Execute the tool with advanced features."""
        # Check cache if enabled
        if self.cache_results and input_text in self.result_cache:
            return self.result_cache[input_text]

        # Apply pre-processors
        processed_input = input_text
        for processor in self.pre_processors:
            processed_input = processor(processed_input)

        # Execute with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._execute(processed_input),
                    timeout=self.timeout
                )
                
                # Apply post-processors
                for processor in self.post_processors:
                    result = processor(result)
                
                # Cache result if enabled
                if self.cache_results:
                    self.result_cache[input_text] = result
                
                return result
                
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout} seconds"
            except Exception as e:
                last_error = str(e)
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(1)  # Wait before retry
        
        raise Exception(f"Failed after {self.max_retries} attempts. Last error: {last_error}")

    def _parse_input(self, input_data: str) -> Dict[str, Any]:
        try:
            # Try to parse as JSON first
            return json.loads(input_data)
        except json.JSONDecodeError:
            # If not JSON, treat as a single parameter
            return {"input": input_data}

    def _validate_parameters(self, params: Dict[str, Any]):
        # Check required parameters
        missing_params = [
            param for param in self.metadata.required_parameters
            if param not in params
        ]
        if missing_params:
            raise ToolError(
                f"Missing required parameters: {', '.join(missing_params)}",
                self.metadata.name,
                "validation"
            )

        # Validate parameter types
        for param, value in params.items():
            if param in self.metadata.parameters:
                expected_type = self.metadata.parameters[param]
                if not isinstance(value, expected_type):
                    raise ToolError(
                        f"Parameter '{param}' must be of type {expected_type.__name__}",
                        self.metadata.name,
                        "validation"
                    )

    async def _execute_with_timeout(self, coro, timeout: float = 30.0) -> Any:
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise ToolError(
                f"Operation timed out after {timeout} seconds",
                self.metadata.name,
                "timeout"
            )

    def log_execution(self, success: bool, execution_time: float, error: Optional[str] = None):
        log_data = {
            "tool": self.metadata.name,
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.error(json.dumps(log_data))

    def add_pre_processor(self, processor: Callable[[str], str]):
        """Add a pre-processor function."""
        self.pre_processors.append(processor)

    def add_post_processor(self, processor: Callable[[str], str]):
        """Add a post-processor function."""
        self.post_processors.append(processor)

    def clear_cache(self):
        """Clear the result cache."""
        self.result_cache.clear() 
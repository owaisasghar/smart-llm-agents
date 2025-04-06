import sys
from io import StringIO
from typing import Dict, Optional, Any
import contextlib

from pydantic import BaseModel, Field
from llm_agents.tools.base import ToolInterface


# Taken from https://github.com/hwchase17/langchain/blob/master/langchain/python.py
class PythonREPL(BaseModel):
    """Simulates a standalone Python REPL."""

    globals: Optional[Dict] = Field(default_factory=dict, alias="_globals")
    locals: Optional[Dict] = Field(default_factory=dict, alias="_locals")

    def run(self, command: str) -> str:
        """Run command with own globals/locals and returns anything printed."""
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(command, self.globals, self.locals)
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            output = str(e)
        return output


def _get_default_python_repl() -> PythonREPL:
    return PythonREPL(_globals=globals(), _locals=None)


class PythonREPLTool(ToolInterface):
    name: str = Field(default="PythonREPLTool", description="Tool for executing Python code")
    description: str = "A tool for executing Python code. Input should be valid Python code."

    async def use(self, code: str) -> str:
        """Execute Python code and return the output."""
        try:
            # Capture stdout and stderr
            stdout = StringIO()
            stderr = StringIO()
            
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                # Execute the code
                exec(code, globals())
            
            # Get the output
            output = stdout.getvalue()
            error = stderr.getvalue()
            
            if error:
                return f"Error: {error}"
            return output or "Code executed successfully but produced no output."
            
        except Exception as e:
            return f"Error executing code: {str(e)}"


if __name__ == '__main__':
    repl_tool = PythonREPLTool()
    result = repl_tool.use('print(5 * 7)')
    assert result == "35\n"
    print(result)

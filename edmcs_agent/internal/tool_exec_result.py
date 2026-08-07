from typing import Any
from dataclasses import dataclass

from langchain_core.messages import ToolMessage


@dataclass(frozen=True)
class ToolExecutionResult:
    '''Internal result produced when the agent executes a tool call.'''

    message: ToolMessage
    result: Any

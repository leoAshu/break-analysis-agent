from typing import Any

from edmcs_agent.contracts import (
    SegmentValidationResult,
    RegionResolutionResult,
)


@staticmethod
def format_tool_args(tool_args: dict) -> str:
    formatted_args = []

    for key, value in tool_args.items():
        display_key = key.removesuffix("_code")
        formatted_args.append(f"{display_key}: {value}")

    return " | ".join(formatted_args)


@staticmethod
def format_tool_result(tool_result: Any) -> str:
    if isinstance(tool_result, SegmentValidationResult):
        return "VALID" if tool_result.is_valid else "INVALID"

    if isinstance(tool_result, RegionResolutionResult):
        return tool_result.region_code

    return str(tool_result)

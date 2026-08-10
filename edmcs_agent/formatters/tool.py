from typing import Any

from edmcs_agent.contracts import (
    SegmentValidationResult,
    RegionResolutionResult,
)


def format_tool_args(tool_args: dict) -> str:
    region = tool_args.get('region_code')

    args = []

    for key, value in tool_args.items():
        if key == 'region_code':
            continue

        display_key = key.removesuffix('_code')
        args.append(f'{display_key}: {value}')

    if region is not None:
        args.append(f'region: {region}')

    return ' | '.join(args)


def format_tool_result(tool_result: Any) -> str:
    if isinstance(tool_result, SegmentValidationResult):
        return 'VALID' if tool_result.is_valid else 'INVALID'

    if isinstance(tool_result, RegionResolutionResult):
        return tool_result.region_code

    return str(tool_result)

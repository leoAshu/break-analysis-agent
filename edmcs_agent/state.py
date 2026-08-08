from typing import TypedDict

from langchain_core.messages import BaseMessage

from edmcs_agent.contracts import (
    BreakRecord,
    InvestigationResult,
    SegmentValidationResult,
    RegionResolutionResult
)


class EDMCSAgentState(TypedDict):
    '''State of the EDMCS agent.'''

    record: BreakRecord
    messages: list[BaseMessage]
    region_resolution: RegionResolutionResult | None
    validation_results: list[SegmentValidationResult]
    missing_segments: list[str]
    is_complete: bool
    result: InvestigationResult | None

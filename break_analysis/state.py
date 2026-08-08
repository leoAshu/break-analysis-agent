from typing import TypedDict

from edmcs_agent.contracts import BreakRecord, InvestigationResult

from break_analysis.contracts import BreakAnalysisResult


class BreakAnalysisState(TypedDict):

    record: BreakRecord
    edmcs_result: InvestigationResult
    result: BreakAnalysisResult

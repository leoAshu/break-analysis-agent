from typing import TypedDict
from enum import StrEnum

from edmcs_agent.contracts import BreakRecord, InvestigationResult

from break_analysis.contracts import BreakAnalysisResult


class AnalysisStatus(StrEnum):
    EXPLAINED = 'explained'
    UNEXPLAINED = 'unexplained'


class BreakAnalysisState(TypedDict):

    record: BreakRecord
    edmcs_result: InvestigationResult
    analysis_status: AnalysisStatus
    explanation: str
    result: BreakAnalysisResult

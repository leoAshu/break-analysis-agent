from edmcs_agent import EDMCSAgent
from edmcs_agent.contracts import BreakRecord

from break_analysis.contracts import BreakAnalysisResult


class BreakAnalysisAgent:
    '''Orchestrates the analysis of a single reconciliation break.'''

    def __init__(self, edmcs_agent: EDMCSAgent) -> None:
        self._edmcs_agent = edmcs_agent

    def analyze(self, record: BreakRecord) -> BreakAnalysisResult:
        edmcs_result = self._edmcs_agent.investigate(record)

        return BreakAnalysisResult(
            record_id=record.record_id,
            is_explained=edmcs_result.is_explained,
            explanation=edmcs_result.summary,
            edmcs_result=edmcs_result,
        )

from edmcs_agent import EDMCSAgent
from edmcs_agent.contracts import BreakRecord

from break_analysis.graph import BreakAnalysisGraph
from break_analysis.contracts import BreakAnalysisResult


class BreakAnalysisAgent:
    '''Orchestrates the analysis of a single reconciliation break.'''

    def __init__(self, edmcs_agent: EDMCSAgent) -> None:
        self._graph = BreakAnalysisGraph(edmcs_agent)


    def analyze(self, record: BreakRecord) -> BreakAnalysisResult:
        state = self._graph.invoke({
            'record': record
        })

        return state['result']

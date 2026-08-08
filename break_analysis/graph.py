from langgraph.graph import END, START, StateGraph

from break_analysis.contracts import BreakAnalysisResult
from break_analysis.state import BreakAnalysisState

from edmcs_agent import EDMCSAgent


class BreakAnalysisGraph:
    '''Defines the workflow for analyzing a reconciliation break.'''

    def __init__(self, edmcs_agent: EDMCSAgent) -> None:
        self._edmcs_agent = edmcs_agent
        self._graph = self._build()


    def invoke(self, state: BreakAnalysisState) -> BreakAnalysisState:
        return self._graph.invoke(state)


    def _investigate_edmcs(self, state: BreakAnalysisState) -> dict:
        edmcs_result = self._edmcs_agent.investigate(state['record'])

        return {
            'edmcs_result': edmcs_result,
        }


    @staticmethod
    def _build_final_result(state: BreakAnalysisState) -> dict:
        edmcs_result = state['edmcs_result']

        return {
            'result': BreakAnalysisResult(
                record_id=state['record'].record_id,
                is_explained=edmcs_result.is_explained,
                explanation=edmcs_result.summary,
                edmcs_result=edmcs_result,
            ),
        }


    def _build(self) -> StateGraph:
        graph = StateGraph(BreakAnalysisState)

        # Nodes
        graph.add_node(
            'investigate_edmcs',
            self._investigate_edmcs,
        )
        graph.add_node(
            'build_final_result',
            self._build_final_result,
        )

        # Edges
        graph.add_edge(
            START,
            'investigate_edmcs',
        )
        graph.add_edge(
            'investigate_edmcs',
            'build_final_result',
        )
        graph.add_edge(
            'build_final_result',
            END,
        )

        return graph.compile()

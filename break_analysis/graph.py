from langgraph.graph import END, START, StateGraph
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from break_analysis.contracts import BreakAnalysisResult
from break_analysis.state import BreakAnalysisState, AnalysisStatus
from break_analysis.prompts import ANALYZE_RESULT_SYSTEM_PROMPT

from edmcs_agent import EDMCSAgent


class BreakAnalysisGraph:
    '''Defines the workflow for analyzing a reconciliation break.'''

    def __init__(self, model: BaseChatModel, edmcs_agent: EDMCSAgent) -> None:
        self._model = model
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
    def _evaluate_edmcs(state: BreakAnalysisState) -> dict:
        edmcs_result = state['edmcs_result']

        status = (
            AnalysisStatus.EXPLAINED 
            if edmcs_result.is_explained 
            else AnalysisStatus.UNEXPLAINED
        )

        return {
            'analysis_status': status,
        }


    def _generate_explanation(self, state: BreakAnalysisState) -> dict:
        edmcs_result = state['edmcs_result']

        messages = [
            SystemMessage(content=ANALYZE_RESULT_SYSTEM_PROMPT),
            HumanMessage(content=edmcs_result.model_dump_json()),
        ]

        explanation = self._model.invoke(messages)

        return {
            'explanation': explanation.content,
        }


    @staticmethod
    def _build_final_result(state: BreakAnalysisState) -> dict:
        record = state['record']
        explanation = state['explanation']
        edmcs_result = state['edmcs_result']
        is_explained = state['analysis_status'] == AnalysisStatus.EXPLAINED

        return {
            'result': BreakAnalysisResult(
                record_id=record.record_id,
                is_explained=is_explained,
                explanation=explanation,
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
            'evaluate_edmcs',
            self._evaluate_edmcs,
        )
        graph.add_node(
            'generate_explanation',
            self._generate_explanation,
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
            'evaluate_edmcs',
        )
        graph.add_edge(
            'evaluate_edmcs',
            'generate_explanation',
        )
        graph.add_edge(
            'generate_explanation',
            'build_final_result',
        )
        graph.add_edge(
            'build_final_result',
            END,
        )

        return graph.compile()

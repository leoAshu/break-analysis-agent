import json
import logging
from typing import Any
from collections.abc import Sequence

from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage, HumanMessage

from edmcs_agent.state import EDMCSAgentState
from edmcs_agent.constants import MAX_RETRIES
from edmcs_agent.contracts import (
    InvestigationResult,
    RegionResolutionResult,
    SegmentValidationResult
)
from edmcs_agent.formatters import (
    format_tool_args,
    format_tool_result
)

from log_utils import (
    log_tool_exec
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EDMCSGraph:
    '''Defines the workflow for investigating a break against EDMCS.'''

    def __init__(self, model: BaseChatModel, tools: Sequence[BaseTool]) -> None:
        self._model = model.bind_tools(list(tools))
        self._tools = {tool.name: tool for tool in tools}
        self._graph = self._build()


    def invoke(self, state: EDMCSAgentState) -> EDMCSAgentState:
        return self._graph.invoke(state)


    # Node
    def _call_model(self, state: EDMCSAgentState) -> dict:
        response = self._model.invoke(state['messages'])

        return {
            'messages': [
                *state['messages'],
                response
            ],
        }


    # Node
    def _execute_tools(self, state: EDMCSAgentState) -> dict:
        response = state['messages'][-1]

        tool_messages = []
        region_resolution = state['region_resolution']
        validation_results = list(state['validation_results'])

        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']

            try:
                tool_result = self._tools[tool_name].invoke(tool_args)
            except KeyError as e:
                tool_result = f'Unknown tool requested: {tool_name}.'
            except Exception as e:
                tool_result = (
                    f'Tool {tool_name} failed with '
                    f'{type(e).__name__}: {str(e)}'
                )

            log_tool_exec(
                logger,
                tool_name=tool_name,
                tool_args=format_tool_args(tool_args),
                tool_result=format_tool_result(tool_result),
            )

            tool_messages.append(
                ToolMessage(
                    content=self._serialize_tool_result(tool_result),
                    tool_call_id=tool_call['id'],
                    name=tool_name,
                )
            )

            if isinstance(tool_result, RegionResolutionResult):
                region_resolution = tool_result

            if isinstance(tool_result, SegmentValidationResult):
                validation_results = self._upsert_validation_result(
                    validation_results,
                    tool_result
                )

        return {
            'messages': [
                *state['messages'],
                *tool_messages
            ],
            'region_resolution': region_resolution,
            'validation_results': validation_results,
        }


    # Node
    @staticmethod
    def _validate_completion(state: EDMCSAgentState) -> dict:
        required_segments = state['record'].segment_values()

        validated_sgements = {
            result.segment_name: result
            for result in state['validation_results']
        }

        missing_segments = sorted(
            set(required_segments) - set(validated_sgements)
        )

        unexpected_segments = sorted(
            set(validated_sgements) - set(required_segments)
        )

        mismatched_segments = sorted(
            segment_name
            for segment_name, result in validated_sgements.items()
            if (
                segment_name in required_segments
                and result.segment_value != required_segments[segment_name]
            )
        )

        is_complete = (
            state['region_resolution'] is not None
            and not missing_segments
            and not unexpected_segments
            and not mismatched_segments
        )

        return {
            'missing_segments': missing_segments,
            'unexpected_segments': unexpected_segments,
            'mismatched_segments': mismatched_segments,
            'is_complete': is_complete,
        }


    # Node
    @staticmethod
    def _request_missing_validations(state: EDMCSAgentState) -> dict:
        missing_items: list[str] = []

        if state['region_resolution'] is None:
            missing_items.append('region resolution')

        if state['missing_segments']:
            missing_items.append(
                'segment validations: '
                + ', '.join(state['missing_segments'])
            )

        if state['unexpected_segments']:
            missing_items.append(
                'remove or correct unexpected validations: '
                + ', '.join(state['unexpected_segments'])
            )

        if state['mismatched_segments']:
            missing_items.append(
                'revalidate segments with incorrect values: '
                + ', '.join(state['mismatched_segments'])
            )

        message = HumanMessage(
            content=(
                'The investigation is incomplete. '
                'Complete the following before providing a final response: '
                + '; '.join(missing_items)
                + '.'
            )
        )

        return {
            'messages': [
                *state['messages'],
                message,
            ],
            'retry_count': state['retry_count'] + 1,
        }


    # Node
    @staticmethod
    def _complete_with_failure(state: EDMCSAgentState) -> dict:
        missing_items: list[str] = []

        if state['region_resolution'] is None:
            missing_items.append('region resolution')

        if state['missing_segments']:
            missing_items.append(
                'segment validations: '
                + ', '.join(state['missing_segments'])
            )

        if state['unexpected_segments']:
            missing_items.append(
                'unexpected segments: '
                + ', '.join(state['unexpected_segments'])
            )

        if state['mismatched_segments']:
            missing_items.append(
                'mismatched segments: '
                + ', '.join(state['mismatched_segments'])
            )

        raise RuntimeError(
            'EDMCS investigation could not complete: '
            + '; '.join(missing_items)
            + '.'
        )


    # Node
    @staticmethod
    def _build_result(state: EDMCSAgentState) -> dict:
        record = state['record']
        summary = state['messages'][-1].content
        validation_results = state['validation_results']
        invalid_segments = EDMCSGraph._get_invalid_segments(validation_results)
        region_code = state['region_resolution'].region_code if state['region_resolution'] else None

        result = InvestigationResult(
            record_id=record.record_id,
            region_code=region_code,
            pre_fah_balance=record.pre_fah_balance,
            gl_balance=record.gl_balance,
            difference=record.difference,
            validations=validation_results,
            is_explained=bool(invalid_segments),
            invalid_segments=invalid_segments,
            summary=summary,
        )

        return {
            'result': result
        }


    # Route
    @staticmethod
    def _route_after_model(state: EDMCSAgentState) -> str:
        response = state['messages'][-1]

        if response.tool_calls:
            return 'execute_tools'

        return 'validate_completion'


    # Route
    @staticmethod
    def _route_after_completion(state: EDMCSAgentState) -> str:
        if state['is_complete']:
            return 'build_result'

        if state['retry_count'] >= MAX_RETRIES:
            return 'complete_with_failure'

        return 'request_missing_validations'


    # Helper
    @staticmethod
    def _serialize_tool_result(result: Any) -> str:
        if isinstance(result, BaseModel):
            return result.model_dump_json()

        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)

        return str(result)


    # Helper
    @staticmethod
    def _get_invalid_segments(
        validation_results: list[SegmentValidationResult],
    ) -> list[str]:
        return [
            result.segment_name
            for result in validation_results
            if not result.is_valid
        ]


    # Helper
    @staticmethod
    def _upsert_validation_result(
        validation_results: list[SegmentValidationResult],
        result: SegmentValidationResult,
    ) -> list[SegmentValidationResult]:
        return [
            existing
            for existing in validation_results
            if existing.segment_name != result.segment_name
        ] + [result]


    # Build the graph
    def _build(self) -> CompiledStateGraph:
        graph = StateGraph(EDMCSAgentState)

        # Nodes
        graph.add_node(
            'call_model',
            self._call_model,
        )
        graph.add_node(
            'execute_tools',
            self._execute_tools,
        )
        graph.add_node(
            'validate_completion',
            self._validate_completion,
        )
        graph.add_node(
            'request_missing_validations',
            self._request_missing_validations,
        )
        graph.add_node(
            'complete_with_failure',
            self._complete_with_failure,
        )
        graph.add_node(
            'build_result',
            self._build_result,
        )
        
        # Edges
        graph.add_edge(
            START,
            'call_model',
        )
        graph.add_conditional_edges(
            'call_model',
            self._route_after_model,
            {
                'execute_tools': 'execute_tools',
                'validate_completion': 'validate_completion',
            }
        )
        graph.add_edge(
            'execute_tools',
            'call_model',
        )
        graph.add_conditional_edges(
            'validate_completion',
            self._route_after_completion,
            {
                'build_result': 'build_result',
                'request_missing_validations': 'request_missing_validations',
                'complete_with_failure': 'complete_with_failure',
            }
        )
        graph.add_edge(
            'request_missing_validations',
            'call_model',
        )
        graph.add_edge(
            'build_result',
            END,
        )

        return graph.compile()

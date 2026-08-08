import json
import logging
from typing import Any
from collections.abc import Sequence

from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage

from edmcs_agent.state import EDMCSAgentState
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

        messages = list(state['messages'])
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

            messages.append(
                ToolMessage(
                    content=self._serialize_tool_result(tool_result),
                    tool_call_id=tool_call['id'],
                    name=tool_name,
                )
            )

            if isinstance(tool_result, RegionResolutionResult):
                region_resolution = tool_result

            if isinstance(tool_result, SegmentValidationResult):
                validation_results.append(tool_result)

        return {
            'messages': messages,
            'region_resolution': region_resolution,
            'validation_results': validation_results,
        }


    # Node
    @staticmethod
    def _build_result(state: EDMCSAgentState) -> dict:
        record = state['record']
        summary = state['messages'][-1].content
        validation_results = state['validation_results']
        invalid_segments = EDMCSGraph._get_invalid_segments(state['validation_results'])
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

        return 'build_result'


    @staticmethod
    def _serialize_tool_result(result: Any) -> str:
        if isinstance(result, BaseModel):
            return result.model_dump_json()

        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)

        return str(result)


    @staticmethod
    def _get_invalid_segments(
        validation_results: list[SegmentValidationResult],
    ) -> list[str]:
        return [
            result.segment_name
            for result in validation_results
            if not result.is_valid
        ]


    # build the graph
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
                'build_result': 'build_result',
            }
        )
        graph.add_edge(
            'execute_tools',
            'call_model',
        )
        graph.add_edge(
            'build_result',
            END,
        )

        return graph.compile()

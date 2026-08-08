import json
import logging
import textwrap
from typing import Any
from collections.abc import Sequence

from pydantic import BaseModel

from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage


from edmcs_agent.prompts import EDMCS_SYSTEM_PROMPT
from edmcs_agent.internal import ToolExecutionResult
from edmcs_agent.contracts import (
    BreakRecord, 
    InvestigationResult, 
    SegmentValidationResult, 
    RegionResolutionResult
)
from edmcs_agent.formatters import (
    format_tool_args, 
    format_tool_result
)

from log_utils import (
    log_agent_start, 
    log_agent_end,
    log_tool_exec
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EDMCSAgent:
    '''Investigate reconciliation breaks using EDMCS validation tools.'''

    NAME = 'EDMCS'

    def __init__(self, model: BaseChatModel, tools: Sequence[BaseTool]) -> None:
        self._tools = {tool.name: tool for tool in tools}
        self._model = model.bind_tools(list(tools))


    def investigate(self, record: BreakRecord) -> InvestigationResult:
        '''
        Investigate a single reconciliation break.

        Resolves the EDMCS region, validates the required GL segments,
        and returns a structured investigation result containing both
        deterministic validation details and a natural-language summary.
        '''
        log_agent_start(logger, agent_name=self.NAME)

        resolved_region: str | None = None
        validation_results: list[SegmentValidationResult] = []

        messages = [
            SystemMessage(content=EDMCS_SYSTEM_PROMPT),
            HumanMessage(content=self._build_user_prompt(record))
        ]

        while True:
            ai_message = self._model.invoke(messages)
            messages.append(ai_message)

            if not ai_message.tool_calls:
                summary = ai_message.content

                result = self._build_investigation_result(
                    record=record,
                    region_code=resolved_region,
                    validation_results=validation_results,
                    summary=summary,
                )

                log_agent_end(
                    logger, 
                    agent_name=self.NAME,
                    is_explained=result.is_explained,
                    invalid_segments=result.invalid_segments
                )
                return result

            for tool_call in ai_message.tool_calls:
                tool_exec = self._execute_tool(tool_call)
                messages.append(tool_exec.message)

                if isinstance(tool_exec.result, RegionResolutionResult):
                    resolved_region = tool_exec.result.region_code

                if isinstance(tool_exec.result, SegmentValidationResult):
                    validation_results.append(tool_exec.result)


    def _execute_tool(self, tool_call: dict) -> ToolExecutionResult:
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
            tool_name, 
            format_tool_args(tool_args), 
            format_tool_result(tool_result)
        )

        return ToolExecutionResult(
            message=ToolMessage(
                content=self._serialize_tool_result(tool_result),
                tool_call_id=tool_call['id'],
                name=tool_name,
            ),
            result=tool_result,
        )
    

    @staticmethod
    def _build_user_prompt(record: BreakRecord) -> str:
        record_lines = [
            f'{field_name} : {field_value}'
            for field_name, field_value in record.segment_values().items()
        ]

        record_text = '\n'.join(record_lines)

        return (
            f'Investigate whether this reconciliation break identified on {record.business_dt} '
            'is explained by invalid EDMCS segment values.\n\n'
            'Record:\n'
            f'{record_text}\n'
            f'future1: {record.future1}\n'
            f'future2: {record.future2}\n'
            f'ledger: {record.ledger}\n'
            f'currency: {record.currency}\n'
            f'pre_fah_balance: {record.pre_fah_balance}\n'
            f'gl_balance: {record.gl_balance}\n'
            f'difference: {record.difference}\n\n'
            'Please provide a detailed explanation of your findings.'
        )


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


    @staticmethod
    def _build_investigation_result(
        record: BreakRecord,
        region_code: str | None,
        validation_results: list[SegmentValidationResult],
        summary: str,
    ) -> InvestigationResult:
        invalid_segments = EDMCSAgent._get_invalid_segments(validation_results)

        return InvestigationResult(
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

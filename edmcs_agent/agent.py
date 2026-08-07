from collections.abc import Sequence

from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from edmcs_agent.contracts import BreakRecord
from edmcs_agent.prompts import EDMCS_SYSTEM_PROMPT

class EDMCSAgent:
    '''Investigate reconciliation breaks using EDMCS validation tools.'''

    def __init__(self, model: BaseChatModel, tools: Sequence[BaseTool]) -> None:
        self._tools = {tool.name: tool for tool in tools}
        self._model = model.bind_tools(list(tools))


    def investigate(self, record: BreakRecord) -> str:
        messages = [
            SystemMessage(content=EDMCS_SYSTEM_PROMPT),
            HumanMessage(content=self._build_user_prompt(record))
        ]

        while True:
            ai_message = self._model.invoke(messages)
            messages.append(ai_message)

            if not ai_message.tool_calls:
                return ai_message.content

            for tool_call in ai_message.tool_calls:
                tool_message = self._execute_tool(tool_call)
                messages.append(tool_message)


    def _execute_tool(self, tool_call: dict) -> ToolMessage:
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

        print(f"{tool_name}({tool_call['args']}) -> {tool_result}")

        return ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"],
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

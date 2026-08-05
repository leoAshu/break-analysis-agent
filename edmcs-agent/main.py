from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage

from models import BreakRecord
from tools import get_region_code, validate_account

def main():
    record = BreakRecord(
        record_id='ROW-101',
        entity='505890',
        dept='A04025',
        branch='000000',
        account='198170',
        sub_account='114110',
        pre_fah_balance=515.67,
        gl_balance=0.00,
        difference=515.67
    )

    tools = {
        get_region_code.name: get_region_code,
        validate_account.name: validate_account
    }

    model = ChatOllama(
        model='qwen3:8b',
        temperature=0
    )
    model_with_tools = model.bind_tools(list(tools.values()))

    messages = [
        HumanMessage(
            content=(
                'Investigate whether the account is valid in EDMCS.\n'
                'First call get_region_code using the entity.\n'
                'Then call validate_account.\n'
                'For validate_account, copy the exact region code returned by '
                'get_region_code. Do not infer, translate, replace, or normalize it.\n\n'
                f'Entity: {record.entity}\n'
                f'Account: {record.account}'
            )
        )
    ]

    while True:
        ai_message = model_with_tools.invoke(messages)
        messages.append(ai_message)

        if not ai_message.tool_calls:
            print('Final response:', ai_message.content)
            break

        for tool_call in ai_message.tool_calls:
            selected_tool = tools[tool_call['name']]
            tool_result = selected_tool.invoke(tool_call['args'])

            print(
                f"{tool_call['name']}({tool_call['args']}) "
                f'-> {tool_result}'
            )

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call['id'],
                )
            )


if __name__ == '__main__':
    main()

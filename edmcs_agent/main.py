from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage

from edmcs_agent.contracts import BreakRecord
from edmcs_agent.tools.mock import create_tools

def main():
    record = BreakRecord(
        record_id='ROW-101',
        business_dt='2026-06-02',

        entity='505890',
        dept='A04025',
        branch='000000',
        account='198170',
        sub_account='114110',
        affiliate='000000',
        book_code='JGAAP_DELTA',
        source='11392:039',
        product='100005',
        project='BILATERAL',
        future1='UNASSIGNED',
        future2='UNASSIGNED',

        ledger='SHARED BD PL',
        currency='USD',

        pre_fah_balance=515.67,
        gl_balance=0.00,
        difference=515.67
    )

    tools = {
        tool.name: tool for tool in
        create_tools()
    }

    model = ChatOllama(
        model='qwen3:8b',
        temperature=0
    )
    model_with_tools = model.bind_tools(list(tools.values()))

    messages = [
        HumanMessage(
            content=(
                'Investigate whether the account and entity in this '
                'reconciliation record are valid in EDMCS.\n\n'
                'Instructions:\n'
                '1. First call get_region_code using the entity.\n'
                '2. Copy the exact region code returned by that tool.\n'
                '3. Use that exact region code to call validate_account.\n'
                '4. Use that same exact region code to call validate_entity.\n'
                '5. Validate both segments even if one validation fails.\n'
                '6. Do not infer, replace, translate, or normalize the '
                'region code.\n'
                '7. After both validations, provide a combined conclusion.\n\n'
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

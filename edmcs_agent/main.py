from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from edmcs_agent.contracts import BreakRecord
from edmcs_agent.tools.mock import create_tools
from edmcs_agent.prompts import EDMCS_SYSTEM_PROMPT

def main():
    record = BreakRecord(
        record_id='ROW-101',
        business_dt='2026-06-02',

        entity='505890',
        department='A04025',
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
        SystemMessage(
            content=EDMCS_SYSTEM_PROMPT
        ),
        HumanMessage(
            content=(
                f'Investigate whether this reconciliation break identified on {record.business_dt} '
                'is explained by invalid EDMCS segment values.\n\n'
                'Record:\n'
                f'Entity: {record.entity}\n'
                f'Department: {record.department}\n'
                f'Branch: {record.branch}\n'
                f'Account: {record.account}\n'
                f'Sub-account: {record.sub_account}\n'
                f'Affiliate: {record.affiliate}\n'
                f'Book code: {record.book_code}\n'
                f'Source: {record.source}\n'
                f'Product: {record.product}\n'
                f'Project: {record.project}\n'
                f'Future1: {record.future1}\n'
                f'Future2: {record.future2}\n'
                f'Ledger: {record.ledger}\n'
                f'Currency: {record.currency}\n'
                f'Pre-FAH balance: {record.pre_fah_balance}\n'
                f'GL balance: {record.gl_balance}\n'
                f'Difference: {record.difference}\n'
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
                f'{tool_call["name"]}({tool_call["args"]}) '
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

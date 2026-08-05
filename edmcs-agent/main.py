from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage

from models import BreakRecord
from tools import get_region_code

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

    model = ChatOllama(
        model='qwen3:8b',
        temperature=0
    )
    model_with_tools = model.bind_tools([get_region_code])

    messages = [
        HumanMessage(
            content=(
                'Find the EDMCS region code for entity '
                f"'{record.entity}'. Use the available tool."
            )
        )
    ]

    # First model call: requests the tool
    ai_message = model_with_tools.invoke(messages)
    messages.append(ai_message)

    tool_call = ai_message.tool_calls[0]

    # Python executes the requested tool
    tool_result = get_region_code.invoke(tool_call['args'])

    # Return the tool result to the model
    messages.append(
        ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call['id'],
        )
    )

    # Second model call: model sees the tool result
    final_response = model_with_tools.invoke(messages)

    print('Tool result:', tool_result)
    print('Final response:', final_response.content)


if __name__ == '__main__':
    main()

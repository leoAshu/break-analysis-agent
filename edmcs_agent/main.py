from langchain_ollama import ChatOllama

from edmcs_agent.agent import EDMCSAgent
from edmcs_agent.contracts import BreakRecord
from edmcs_agent.tools.mock import create_tools


def main():
    model = ChatOllama(
        model='qwen3:8b',
        temperature=0
    )

    tools = create_tools()

    agent = EDMCSAgent(
        model=model, 
        tools=tools
    )

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

    response = agent.investigate(record)
    print('Final response:\n', response)
    

if __name__ == '__main__':
    main()

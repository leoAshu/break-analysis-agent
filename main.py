import logging

from langchain_ollama import ChatOllama

from edmcs_agent import EDMCSAgent
from edmcs_agent.contracts import BreakRecord
from edmcs_agent.tools.mock import create_tools

from break_analysis import BreakAnalysisAgent


logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(name)-24s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger(__name__).setLevel(logging.INFO)


def main():
    model = ChatOllama(
        model='qwen3:8b',
        temperature=0
    )

    tools = create_tools()

    edmcs_agent = EDMCSAgent(
        model=model, 
        tools=tools
    )

    agent = BreakAnalysisAgent(
        model=model,
        edmcs_agent=edmcs_agent
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
        source='11392:0397',
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

    agent.analyze(record)
    

if __name__ == '__main__':
    main()

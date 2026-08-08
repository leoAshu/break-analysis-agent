import logging
from collections.abc import Sequence

from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from edmcs_agent.graph import EDMCSGraph
from edmcs_agent.state import EDMCSAgentState
from edmcs_agent.prompts import EDMCS_SYSTEM_PROMPT
from edmcs_agent.contracts import (
    BreakRecord, 
    InvestigationResult, 
)

from log_utils import (
    log_agent_start, 
    log_agent_end,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EDMCSAgent:
    '''Investigate reconciliation breaks using EDMCS validation tools.'''

    NAME = 'EDMCS'

    def __init__(self, model: BaseChatModel, tools: Sequence[BaseTool]) -> None:
        self._graph = EDMCSGraph(
            model=model, 
            tools=tools
        )


    def investigate(self, record: BreakRecord) -> InvestigationResult:
        '''
        Investigate a single reconciliation break.

        Resolves the EDMCS region, validates the required GL segments,
        and returns a structured investigation result containing both
        deterministic validation details and a natural-language summary.
        '''
        log_agent_start(logger, agent_name=self.NAME)

        messages = [
            SystemMessage(content=EDMCS_SYSTEM_PROMPT),
            HumanMessage(content=self._build_user_prompt(record))
        ]

        initial_state: EDMCSAgentState = {
            'record': record,
            'messages': messages,
            'region_resolution': None,
            'validation_results': [],
            'missing_segments': [],
            'is_complete': False,
            'retry_count': 0,
            'result': None
        }

        state = self._graph.invoke(initial_state)

        result: InvestigationResult = state['result']

        if result is None:
            raise RuntimeError(
                'EDMCS investigation failed to produce a result.'
            )

        log_agent_end(
            logger,
            agent_name=self.NAME,
            is_explained=result.is_explained,
            invalid_segments=result.invalid_segments,
        )

        return result
    

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

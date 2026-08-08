import textwrap
from logging import Logger

from edmcs_agent.contracts import BreakRecord


WIDTH = 80


def log_analysis_start(logger: Logger, record: BreakRecord) -> None:
    logger.info('=' * WIDTH)
    logger.info(
        'ANALYSIS START | id: %s | date: %s | diff (%s): %s',
        record.record_id,
        record.business_dt,
        record.currency,
        record.difference,
    )
    logger.info('=' * WIDTH)
    logger.info('')


def log_dispatch_agent(logger: Logger, agent_name: str, reason: str) -> None:
    logger.info('DISPATCH | agent: %s | reason: %s', agent_name, reason)
    logger.info('')


def log_agent_start(logger: Logger, agent_name: str) -> None:
    logger.info('+' * WIDTH)
    logger.info('AGENT START | %s', agent_name)
    logger.info('-' * WIDTH)
    logger.info('')


def log_agent_end(logger: Logger, agent_name: str, is_explained: bool, invalid_segments: list) -> None:
    logger.info('')
    logger.info('-' * WIDTH)
    logger.info(
        'AGENT COMPLETE | %s | explained: %s | invalid: %s',
        agent_name,
        is_explained,
        invalid_segments or 'None',
    )
    logger.info('+' * WIDTH)


def log_analysis_complete(logger: Logger, record_id: str, is_explained: bool, explanation: str) -> None:
    logger.info('')
    logger.info('=' * WIDTH)
    logger.info(
        'ANALYSIS COMPLETE | id: %s | explained: %s',
        record_id,
        is_explained,
    )

    logger.info('-' * WIDTH)
    logger.info('SUMMARY')
    for paragraph in explanation.splitlines():
        for line in textwrap.wrap(paragraph.strip(), width=WIDTH - 6):
            logger.info('%s', line)

    logger.info('=' * WIDTH)

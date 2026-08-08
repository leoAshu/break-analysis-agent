from logging import Logger


def log_tool_exec(logger: Logger, tool_name: str, tool_args: str, tool_result: str) -> None:
    logger.info(
        'TOOL | %-20s | %-36s | %s',
        tool_name,
        tool_args,
        tool_result,
    )

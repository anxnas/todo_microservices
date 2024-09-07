from profi_log import MasterLogger
from config import settings

def get_logger(name: str) -> MasterLogger:
    logger = MasterLogger(
        f"logs/{name}.log",
        level=settings.LOG_LEVEL
    )
    logger.setup_colored_console_logging()
    return logger
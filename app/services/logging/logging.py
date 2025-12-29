import logging

def get_logger(logger_name: str = None, level: str = "INFO"):
    """
    Универсальный логгер приложения.

    Args:
        logger_name (str): имя логгера (обычно __name__)
        level (str): уровень логирования (INFO / DEBUG / WARNING / ERROR)

    Returns:
        logging.Logger: настроенный логгер
    """

    # Приводим уровни в корректный формат
    if isinstance(level, str):
        level = level.upper()

    # Инициализация basicConfig вызывается один раз
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    return logger

from logging import Logger as loggingLogger
from .logger import Logger
from ...config.variables import LoggerDef, LoggerSystemDef


class LoggerFactory:
    @staticmethod
    def new_logger(
        name=None, level=None, fmt=None, directory=None, log_to_console=False
    ):
        return Logger(name, level, fmt, directory, log_to_console)

    @staticmethod
    def new_logger_get_logger(
        name=None, level=None, fmt=None, directory=None, log_to_console=False
    ):
        if not directory:
            directory = "logs"
        return Logger.new_get_logger(name, level, fmt, directory, log_to_console)

    @staticmethod
    def new_logger_default(
        name=None, level=None, fmt=None, directory=None, log_to_console=False
    ):
        if not directory:
            directory = f"{LoggerDef.ROOT_DIR}/logger"
        if not fmt:
            fmt = LoggerDef.FORMAT
        return Logger.new_get_logger(name, level, fmt, directory, log_to_console)

    @staticmethod
    def new_logger_flask(app, name, level, fmt, directory, log_to_console=False):
        logger = Logger(name, level, fmt, directory, log_to_console)
        file_handler = logger.create_file_handler(name, level, fmt, directory)
        app.logger.addHandler(file_handler)
        return app.logger

    @staticmethod
    def new_logger_system(name, level, fmt, directory, log_to_console=False):
        return Logger.new_get_logger(name, level, fmt, directory, log_to_console)

"""Logger class."""
import logging
import os
import sys


class Logger:
    def __init__(
        self, name=None, level=None, fmt=None, directory=None, log_to_console=False
    ):
        # properties
        self.name = name
        self.level = level
        self.fmt = fmt
        self.directory = directory
        self.log_to_console = log_to_console
        # objects
        self.logger = None
        self.file_handler = None

    # Additional Method
    def set_up_logger(self, name=None, level=None, fmt=None):
        if name is None:
            name = self.name
        if level is None:
            level = self.level
        if fmt is None:
            fmt = self.fmt
            if fmt is None:
                fmt = "simple"

        self.logger = self.set_logger(name, level, fmt)
        return self.logger

    def set_logger(self, name, level, fmt):
        logger = logging.getLogger(name)

        if level is None:
            level = self.level
            if self.level is None:
                level = logging.INFO
        else:
            level = self.parse_level(level)
        logger.setLevel(level)

        if not fmt:
            fmt = self.fmt
            if not fmt:
                fmt = "simple"
        formatter = self.set_formatter_format(fmt)

        path = f"{self.directory}/{name}.log"
        # print(f"Using {path} as the log file")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        fileh = logging.FileHandler(path, "a")
        fileh.setFormatter(formatter)
        logger.addHandler(fileh)

        if self.log_to_console:
            # Add stdout handler
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(formatter)
            logger.addHandler(stdout_handler)

            # Optionally, add stderr handler for certain log levels
            if level >= logging.ERROR:
                stderr_handler = logging.StreamHandler(sys.stderr)
                stderr_handler.setFormatter(formatter)
                logger.addHandler(stderr_handler)

        return logger

    def set_formatter_format(self, option=None):
        options = ["simple", "process", "function", "fun"]
        if option not in options:
            raise ValueError(
                f"Invalid option for formatter format: {option}. Valid options are {options}."
            )

        if option == "simple":
            return logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        if option == "process":
            return logging.Formatter(
                "%(asctime)s %(module)s -> %(process)d -  %(message)s"
            )
        if option == "function":
            return logging.Formatter(
                "%(asctime)s %(module)s %(funcName)s -  %(message)s"
            )
        if option == "fun":
            return FormatterWithEmoji(
                "%(asctime)s %(module)s %(funcName)s -  %(message)s"
            )

    def get_logger(self, name=None, level=None, fmt=None, directory=None):
        if self.logger is None:
            self.set_up_logger(name, level, fmt)
        return self.logger

    def create_file_handler(self, name=None, level=None, fmt=None, directory=None):
        if name is None:
            name = self.name
            if not name:
                print("Logger name not set. Cannot create file handler.")
                return None
        if not level:
            level = self.level
        if not fmt:
            fmt = self.set_formatter_format(self.fmt)
        if not directory:
            directory = self.directory
            if not directory:
                directory = "./"  # default directory if not set
        # create file handler
        logger_directory = f"{directory}/{name}.log"
        _file_handler = logging.FileHandler(logger_directory)
        _file_handler.setLevel(self.parse_level(level))
        _file_handler.setFormatter(fmt)
        self.file_handler = _file_handler
        return self.file_handler

    @staticmethod
    def parse_level(level):  # defaults to info
        if level is None:
            return logging.INFO
        if level == "DEBUG":
            return logging.DEBUG
        if level == "INFO":
            return logging.INFO
        if level == "WARNING":
            return logging.WARNING
        if level == "ERROR":
            return logging.ERROR
        if level == "CRITICAL":
            return logging.CRITICAL
        return logging.INFO

    def __str__(self) -> str:
        return f"Logger: {self.__dict__}"

    @staticmethod
    def new(name=None, level=None, fmt=None, directory=None, log_to_console=False):
        return Logger(name, level, fmt, directory, log_to_console)

    @staticmethod
    def new_get_logger(
        name=None, level=None, fmt=None, directory=None, log_to_console=False
    ):
        logger = Logger.new(name, level, fmt, directory, log_to_console)
        return logger.get_logger()


class FormatterWithEmoji(logging.Formatter):
    emoji_mapping = {
        "DEBUG": "🐛",
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.emoji_mapping:
            record.msg = f"{self.emoji_mapping[levelname]} {record.msg}"
        return super().format(record)

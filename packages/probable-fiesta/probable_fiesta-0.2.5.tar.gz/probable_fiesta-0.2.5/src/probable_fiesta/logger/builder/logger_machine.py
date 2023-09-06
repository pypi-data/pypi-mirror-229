from abc import ABC, abstractmethod

from ...config.variables import LoggerDef, LoggerSystemDef
from .logger_factory import LoggerFactory


# Abstract Log Factory
class AbstractLogFactory(ABC):
    @abstractmethod
    def create_logger(self, name, level, fmt, directory):
        pass


# Concrete Log Factories
class DockerLogFactory(AbstractLogFactory):
    def create_logger(self, name, level, fmt, directory):
        return LoggerFactory.new_logger(
            name, level, fmt, directory, log_to_console=True
        )


class DefaultLogFactory(AbstractLogFactory):
    def create_logger(
        self,
        name,
        level=LoggerDef.LEVEL,
        fmt=LoggerDef.FORMAT,
        directory=LoggerDef.DIRECTORY,
        log_to_console=False,
    ):
        return LoggerFactory.new_logger_default(
            name, level, fmt, directory, log_to_console
        )


class FlaskLogFactory(AbstractLogFactory):
    def create_logger(self, app, name, level, fmt, directory):
        return LoggerFactory.new_logger_flask(app, name, level, fmt, directory)


class SystemLogFactory(AbstractLogFactory):
    def create_logger(
        self,
        name=LoggerSystemDef.NAME,
        level=LoggerSystemDef.LEVEL,
        fmt=LoggerSystemDef.FORMAT,
        directory=LoggerSystemDef.DIRECTORY,
        log_to_console=True,
    ):
        return LoggerFactory.new_logger_system(
            name, level, fmt, directory, log_to_console
        )

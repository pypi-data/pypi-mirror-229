from .config_builder import ConfigBuilder
from ...logger.builder.logger_machine import DefaultLogFactory, DockerLogFactory
from ..variables import PackageDef as pd
from ..variables import LoggerDef as ld
from ..variables import VariablesDef as vd
from ..variables import DotEnvDef as ded


class ConfigFactory:
    @staticmethod
    def new_config_builder():
        return ConfigBuilder()

    @staticmethod
    def new_config():
        return ConfigBuilder().build()

    @staticmethod
    def new_default_config_builder(log_type="default", log_name="default"):
        if not log_type:
            log_type = "default"
        if log_type == "default":
            logger_factory = DefaultLogFactory()
            logger = logger_factory.create_logger(
                log_name, ld.LEVEL, ld.FORMAT, ld.DIRECTORY
            )
        if log_type == "docker":
            logger_factory = DockerLogFactory()
            logger = logger_factory.create_logger(
                log_name, ld.LEVEL, ld.FORMAT, ld.DIRECTORY
            )
        cB = ConfigBuilder()
        config = (
            cB.package.set_package_name(pd.NAME)
            .logger.set_logger(logger)
            .variables.set_variable("VERSION", vd.VERSION)
            .dotenv.load_dotenv()
            .set_vars(ded().__dict__)  # Only public variables are loaded
            .build()
        )
        return config

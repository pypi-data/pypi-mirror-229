from src.probable_fiesta.logger.builder import logger_factory
from src.probable_fiesta.logger.builder.logger_machine import (
    DockerLogFactory,
    DefaultLogFactory,
    FlaskLogFactory,
    SystemLogFactory,
)
from src.probable_fiesta.config.variables import LoggerDef, LoggerSystemDef
from unittest import TestCase


class TestLoggerFactories(TestCase):
    def setUp(self):
        self.logger_factory = logger_factory.LoggerFactory()

    def test_docker_log_factory(self):
        print("Test DockerLogFactory")
        factory = DockerLogFactory()
        logger = factory.create_logger("test", "INFO", "simple", "logs")
        self.validate_logger(
            logger,
            name="test",
            level="INFO",
            fmt="simple",
            directory="logs",
            log_to_console=True,
        )

    def test_default_log_factory(self):
        print("Test DefaultLogFactory")
        factory = DefaultLogFactory()
        logger = factory.create_logger("default_logger")
        name = "default_logger"
        level = 20
        self.assertEqual(logger.name, name)
        self.assertEqual(logger.level, level)

    # def test_flask_log_factory(self):
    #    print("Test FlaskLogFactory")
    #    app = "Your Flask App Here"  # Replace with an actual Flask app instance
    #    factory = FlaskLogFactory()
    #    logger = factory.create_logger(app, "test", "INFO", "simple", "logs")
    # You may need to further validate the Flask logger as needed

    def test_system_log_factory(self):
        print("Test SystemLogFactory")
        factory = SystemLogFactory()
        logger = factory.create_logger()
        name = LoggerSystemDef.NAME
        level = 20
        self.assertEqual(logger.name, name)
        self.assertEqual(logger.level, level)

    def validate_logger(self, logger, name, level, fmt, directory, log_to_console):
        self.assertEqual(logger.name, name)
        self.assertEqual(logger.level, level)
        self.assertEqual(logger.fmt, fmt)
        self.assertEqual(logger.directory, directory)
        self.assertEqual(logger.log_to_console, log_to_console)
        self.assertIsNone(logger.logger)
        self.assertIsNone(logger.file_handler)

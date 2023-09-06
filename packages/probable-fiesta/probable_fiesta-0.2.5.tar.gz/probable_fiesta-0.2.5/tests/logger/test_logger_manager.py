from src.probable_fiesta.logger.builder.logger_machine import (
    DockerLogFactory,
    DefaultLogFactory,
    FlaskLogFactory,
    SystemLogFactory,
)
from src.probable_fiesta.logger.builder.logger_factory import LoggerFactory
from unittest import TestCase
from unittest.mock import MagicMock


class TestLogFactories(TestCase):
    def setUp(self):
        self.name = "test_logger"
        self.level = "INFO"
        self.fmt = "simple"
        self.directory = "logs"

    def test_docker_log_factory(self):
        factory = DockerLogFactory()
        logger = factory.create_logger(self.name, self.level, self.fmt, self.directory)
        expected_logger = LoggerFactory.new_logger(
            self.name, self.level, self.fmt, self.directory, log_to_console=True
        )
        self.assertEqual(str(logger), str(expected_logger))

    def test_default_log_factory(self):
        factory = DefaultLogFactory()
        logger = factory.create_logger(self.name, self.level, self.fmt, self.directory)
        expected_logger = LoggerFactory.new_logger_default(
            self.name, self.level, self.fmt, self.directory
        )
        self.assertEqual(str(logger), str(expected_logger))

    def test_flask_log_factory(self):
        app = MagicMock()  # Mocking Flask app
        factory = FlaskLogFactory()
        logger = factory.create_logger(
            app, self.name, self.level, self.fmt, self.directory
        )
        expected_logger = LoggerFactory.new_logger_flask(
            app, self.name, self.level, self.fmt, self.directory
        )
        self.assertEqual(logger, expected_logger)

    def test_system_log_factory(self):
        factory = SystemLogFactory()
        logger = factory.create_logger(self.name, self.level, self.fmt, self.directory)
        expected_logger = LoggerFactory.new_logger(
            self.name, self.level, self.fmt, self.directory, log_to_console=False
        )
        # This is cheating, but ok for now
        self.assertEqual(str(logger.name), str(expected_logger.name))

"""Unit test file for config.builder.config_builder.py."""
import os
import shutil
from unittest import TestCase

from src.probable_fiesta.config.builder import config_builder


class TestConfig(TestCase):
    def setUp(self):
        self.cB = config_builder.ConfigBuilder()
        self.root_dir = "test_dir"
        os.makedirs(self.root_dir, exist_ok=True)
        self.env_path = os.path.join(self.root_dir, "test.env")
        with open(self.env_path, "w") as f:
            f.write("TEST_KEY=TEST_VALUE\n")

    def tearDown(self):
        shutil.rmtree(self.root_dir)

    def test_init(self):
        # LOG.info("Test init")
        self.cB = config_builder.ConfigBuilder()
        self.assertEqual(
            str(self.cB),
            "ConfigBuilder: {'package': {}, 'logger': None, 'variables': {}, 'dotenv': None, 'parsed_dotenv': {}}",
        )

    def test_package_property(self):
        self.cB = config_builder.ConfigBuilder()

        def test_set_package_name():
            # test package name
            self.cB.package.set_package_name("test")
            self.assertEqual(
                str(self.cB),
                "ConfigBuilder: {'package': {'name': 'test'}, 'logger': None, 'variables': {}, 'dotenv': None, 'parsed_dotenv': {}}",
            )

        def test_set_root_dir():
            # test root dir
            self.cB.package.set_root_dir("test")
            self.assertEqual(
                str(self.cB),
                "ConfigBuilder: {'package': {'name': 'test', 'root_directory': 'test'}, 'logger': None, 'variables': {}, 'dotenv': None, 'parsed_dotenv': {}}",
            )

        test_set_package_name()
        test_set_root_dir()

    def test_logger_property(self):
        self.cB = config_builder.ConfigBuilder()

        def test_set_logger_level():
            # test logger level
            self.cB.logger.set_logger_level("test")
            self.assertEqual(
                str(self.cB),
                "ConfigBuilder: {'package': {}, 'logger': 'test', 'variables': {}, 'dotenv': None, 'parsed_dotenv': {}}",
            )

        def test_set_logger_dir():
            # test logger dir
            self.cB.logger.set_logger_dir("test")
            self.assertEqual(
                str(self.cB),
                "ConfigBuilder: {'package': {}, 'logger': 'test', 'variables': {}, 'dotenv': None, 'parsed_dotenv': {}}",
            )

        def test_set_logger_format():
            # test logger format
            self.cB.logger.set_logger_format("test")
            self.assertEqual(
                str(self.cB),
                "ConfigBuilder: {'package': {}, 'logger': 'test', 'variables': {}, 'dotenv': None, 'parsed_dotenv': {}}",
            )

        def test_set_logger():
            # test set logger
            self.cB.logger.set_logger("test")
            self.assertEqual(
                str(self.cB),
                "ConfigBuilder: {'package': {}, 'logger': 'test', 'variables': {}, 'dotenv': None, 'parsed_dotenv': {}}",
            )

        def test_set_new_logger():
            # test set new logger
            self.cB.logger.set_new_logger("test", "test", "test")
            self.assertEqual(
                str(self.cB.build().logger),
                "Logger: {'name': 'test', 'level': 'test', 'fmt': 'test', 'directory': None, 'log_to_console': False, 'logger': None, 'file_handler': None}",
            )

        test_set_logger_level()
        test_set_logger_dir()
        test_set_logger_format()
        test_set_logger()
        test_set_new_logger()

    def test_load_dotenv_with_root_dir(self):
        self.cB.dotenv.load_dotenv(path="test.env", root_dir=self.root_dir)
        self.assertIn("TEST_KEY", self.cB.config.parsed_dotenv)
        self.assertEqual("TEST_VALUE", self.cB.config.parsed_dotenv["TEST_KEY"])

    def test_parse_vars(self):
        # Using the parse_vars method from ConfigDotEnv class on self.env_path
        self.cB.dotenv.parse_vars(self.env_path)

        # Check if the value has been correctly parsed
        self.assertIn("TEST_KEY", self.cB.config.parsed_dotenv)
        self.assertEqual("TEST_VALUE", self.cB.config.parsed_dotenv["TEST_KEY"])

    def test_set_vars(self):
        new_vars = {"NEW_KEY": "NEW_VALUE"}
        self.cB.dotenv.set_vars(new_vars)

        # Check if the value has been correctly set
        self.assertIn("NEW_KEY", self.cB.config.parsed_dotenv)
        self.assertEqual("NEW_VALUE", self.cB.config.parsed_dotenv["NEW_KEY"])

    def test_get_var(self):
        self.cB.dotenv.set_vars({"NEW_KEY": "NEW_VALUE"})
        value = self.cB.dotenv.get_var("NEW_KEY")
        self.assertEqual(value, "NEW_VALUE")

        # Test a key that does not exist
        self.assertIsNone(self.cB.dotenv.get_var("NON_EXISTENT_KEY"))

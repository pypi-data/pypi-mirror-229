"""Unit test file for command.builder.command.py."""
from src.probable_fiesta.command.builder import command
from src.probable_fiesta.logger.logging_config import set_logger

from logging import DEBUG
from unittest import TestCase

# Create a logger
LOG = set_logger("test_command", DEBUG)


import pytest

from src.probable_fiesta.command.builder import command


class TestCommand(TestCase):
    def test_init_valid(self):
        name = "test"
        func = lambda x: x
        args = (1, 2, 3)

        cmd = command.Command(name, func, *args)

        assert cmd.name == name
        assert cmd.function == func
        assert cmd.args == args

    def test_invoke_valid(self):
        # Setup
        func = lambda x, y: x**y
        cmd = command.Command("square", func, 3, 2)

        # Invoke
        result = cmd.invoke()

        # Assertions
        self.assertEqual(result, 9)


class TestCommandBuilderCommand(TestCase):
    def setUp(self):
        self.command = None

    def test_init(self):
        self.command = command.Command(None, None, None)
        self.assertEqual(self.command.name, None)
        self.assertEqual(self.command.function, None)
        self.assertEqual(self.command.args, (None,))

    def test_init_with_args(self):
        function = lambda: "Hello World!"
        self.command = command.Command("test", function, "--version")
        self.assertEqual(self.command.name, "test")
        self.assertEqual(self.command.function, function)
        self.assertEqual(self.command.args, ("--version",))

    def test_factory(self):
        function = lambda: "Hello World!"
        self.command = command.CommandFactory.new_command("test", function, "--version")
        self.assertEqual(self.command.name, "test")
        self.assertEqual(self.command.function, function)
        self.assertEqual(self.command.args, ("--version",))

    def test_invoke(self):
        function = lambda x: x
        self.command = command.Command("test", function, None)
        result = self.command.invoke()
        self.assertEqual(result, None)

    def test_invoke_with_args(self):
        args = "--version"
        function = lambda x: x
        self.command = command.Command("test", function, args)
        result = self.command.invoke()
        self.assertEqual(result, args)

    def test_invoke_without_function(self):
        self.command = command.Command(None, None, None)
        with pytest.raises(TypeError):
            self.command.invoke()

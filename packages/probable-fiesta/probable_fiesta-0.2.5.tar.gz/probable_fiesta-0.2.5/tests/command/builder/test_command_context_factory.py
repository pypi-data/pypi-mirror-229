"""Unit test file for command_context_factory.py."""
import unittest
from src.probable_fiesta.app.builder.command_context_factory import (
    CommandContextFactory,
)
from src.probable_fiesta.app.builder.app_builder import AppBuilder
from src.probable_fiesta.command.builder.command_factory import CommandFactory
from src.probable_fiesta.command.builder.command_queue import CommandQueue


class TestCommandContextFactory(unittest.TestCase):
    def setUp(self):
        self.app_builder = AppBuilder()

    def test_command_context_factory(self):
        def sample_function(a, b):
            return str(a + b)

        context_name = "sample_context"
        command_name = "sample_command"
        arg1, arg2 = 1, 2

        # Create a CommandContext object with the command
        command_context = CommandContextFactory.create_command_context(
            context_name, command_name, sample_function, arg1, arg2
        )

        self.app_builder.context.add_context(command_context)

        # Run the created command
        app = self.app_builder.build()
        app.run(context_name)

        # Check the output
        stdout = app.get_run_history()

        print("Actual output:", stdout)  # Add this print statement for debugging

        expected_output = sample_function(arg1, arg2)
        print(
            "Expected output:", expected_output
        )  # Add this print statement for debugging

        self.assertEqual(stdout, expected_output)

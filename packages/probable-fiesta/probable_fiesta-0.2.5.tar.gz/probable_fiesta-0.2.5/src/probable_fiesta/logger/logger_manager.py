from .builder.logger_machine import (
    DockerLogFactory,
    FlaskLogFactory,
    SystemLogFactory,
    DefaultLogFactory,
)


class LogManager:
    def __init__(self):
        self.factories = {
            "docker": DockerLogFactory(),
            "default": DefaultLogFactory(),
            "flask": FlaskLogFactory(),
            "system": SystemLogFactory(),
        }

    def create_logger(self, logger_type, *args, **kwargs):
        factory = self.factories.get(logger_type)
        if factory is None:
            raise ValueError(f"Unknown logger type: {logger_type}")

        return factory.create_logger(*args, **kwargs)

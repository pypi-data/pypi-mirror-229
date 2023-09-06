from os.path import join, realpath, exists
from dotenv import load_dotenv as ld_env
from ...logger.builder.logger_factory import LoggerFactory
from .config import Config


class ConfigBuilder:
    def __init__(self, config=None):
        if config is None:
            self.config = Config()
        else:
            self.config = config

    def __str__(self):
        return f"ConfigBuilder: {self.config.__dict__}"

    @property
    def package(self):
        return ConfigPackage(self.config)

    @property
    def logger(self):
        return ConfigLogger(self.config)

    @property
    def variables(self):
        return ConfigVariables(self.config)

    @property
    def dotenv(self):
        return ConfigDotEnv(self.config)

    def build(self):
        return self.config


class ConfigPackage(ConfigBuilder):
    def __init__(self, config):
        super().__init__(config)

    def set_package_name(self, name):
        self.config.package["name"] = name
        return self

    def set_root_dir(self, directory):
        self.config.package["root_directory"] = directory
        return self


class ConfigLogger(ConfigBuilder):
    def __init__(self, config):
        super().__init__(config)

    def set_logger_level(self, level):
        self.config.logger = level
        return self

    def set_logger_dir(self, directory):
        self.config.logger = directory
        return self

    def set_logger_format(self, log_format):
        self.config.logger = log_format
        return self

    def set_logger_name(self, name):
        self.config.logger.name = name
        return self

    def set_logger(self, logger):
        self.config.logger = logger
        return self

    def set_new_logger(self, name=None, level=None, fmt=None, directory=None):
        self.config.logger = LoggerFactory.new_logger(name, level, fmt, directory)
        return self


class ConfigVariables(ConfigBuilder):
    def __init__(self, config):
        super().__init__(config)

    def set_variable(self, name, value):
        self.config.variables[name] = value
        return self

    def set_variables(self, variables):
        self.config.variables.update(variables)
        return self

    def get_from_module_config(self):
        self.config.variables.update(self.config.variables.module_config)
        return self


class ConfigDotEnv(ConfigBuilder):
    def __init__(self, config):
        super().__init__(config)

    def load_dotenv(self, path=".env", root_dir="."):
        # First, try to load the .env file from the given path
        if ld_env(path):
            print(".env file loaded successfully from the given path")
            self.parse_vars(path)
        else:
            # If not found or couldn't load from given path,
            # determine absolute path of the .env file using the provided root_dir
            abs_path = realpath(join(root_dir, path))

            # Use python-dotenv's load_dotenv method for the absolute path
            if ld_env(abs_path):
                print(".env file loaded successfully from absolute path")
                self.parse_vars(abs_path)
            else:
                print(
                    f"Warning: Unable to find .env file at both {path} and {abs_path}"
                )

        return self

    def parse_vars(self, path):
        try:
            with open(path) as f:
                for line in f:
                    key, value = line.strip().split("=", 1)
                    if (
                        key not in self.config.parsed_dotenv
                    ):  # check if key is not already in the dictionary
                        self.config.parsed_dotenv[key] = value
        except IOError:
            print(f"Warning: Unable to open .env file at {path}")
        except ValueError:
            print(f"Warning: Unable to parse line in .env file: {line}")

    def set_vars(self, vars):
        self.config.parsed_dotenv.update(vars)
        return self

    def get_var(self, var_name):
        if var_name in self.config.parsed_dotenv:
            return self.config.parsed_dotenv[var_name]
        return None

import inspect


class Command:
    def __init__(self, name, function, *args):
        self.name = name
        self.function = function
        self.args = args

    def __str__(self):
        return f"Command: {self.__dict__}"

    def invoke(self, input=None):
        if not isinstance(self.name, str):
            raise TypeError(f"Name must be a string, got {type(self.name)}")

        if not callable(self.function):
            raise TypeError(f"Function must be callable, got {type(self.function)}")

        if not isinstance(self.args, tuple):
            raise TypeError(f"Args must be a tuple, got {type(self.args)}")

        if self.function is not None:
            num_args = len(inspect.signature(self.function).parameters)

            if num_args == 0:
                return self.function()
            elif num_args == 1:
                if input is not None:
                    return self.function(input)
                elif self.args:
                    return self.function(*self.args)
            else:
                if input is not None:
                    return self.function(input, *self.args)
                else:
                    return self.function(*self.args)

        return None


class CommandFactory:
    @staticmethod
    def new_command(name, function, *args):
        return Command(name, function, *args)

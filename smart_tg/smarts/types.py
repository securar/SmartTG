import warnings
from typing import Coroutine, Callable

from pydantic import BaseModel

from telethon import TelegramClient
from telethon.events import NewMessage

from config import PREFIX


class _ModuleFunc(BaseModel):
    command: str
    description: str
    func: Callable[[NewMessage.Event, TelegramClient], Coroutine]


class SmartModuleController:
    """
    **Controller for creating modules**
    """

    def __init__(self, name: str, description: str):
        """

        :param name: Module name
        :param description: Module description, what module can do
        """
        self.name = name
        self.description = description
        self._modulefuncs: list[_ModuleFunc] = []

    @staticmethod
    def _is_prefix_in_command(command: str) -> bool:
        return PREFIX in command

    @staticmethod
    def _ensure_prefix_absence(command: str) -> str:
        return command.replace(PREFIX, "")

    def modulefunc(self, command: str, description: str):
        # Fake decorator to get arguments.
        """
        Decorator for module functions.

        **Use it to bind the function to the controller.**

        :param command: Command for usage in telegram **(without prefix)**
        :param description: Description, what function can do
        :return:
        """

        def _actual_decorator(func: Callable[[NewMessage.Event, TelegramClient], Coroutine]):
            def wrapper(*args, **kwargs):
                if self._is_prefix_in_command(command=command):
                    warnings.warn(
                        "Looks like you have passed \"command\" argument with prefix in it\n"
                        "You don't have to do that. It is not critical, but it is better not to do it\n"
                        "\n"
                        "P.S. if you want to separate words in a command - use underscores\n"
                    )
                clean_command = self._ensure_prefix_absence(command=command)
                self._modulefuncs.append(
                    _ModuleFunc(
                        command=clean_command,
                        description=description,
                        func=func
                    )
                )
                return func(*args, **kwargs)

            return wrapper

        return _actual_decorator

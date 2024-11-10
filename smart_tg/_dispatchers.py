import inspect
import warnings
import importlib

from types import ModuleType
from typing import Literal, Union
from string import ascii_lowercase
from asyncio.exceptions import CancelledError

from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.sessions import StringSession

from smart_tg import exceptions, html, markdown
from smart_tg.enums import ParseMode
from smart_tg.types import ModuleFunction, FuncType, Event, CommandArgs
from smart_tg._loggers import core_logger
from smart_tg._constants import (
    BAD_PREFIXES,
    MODULE_SHOULD_ENDS_WITH,
    CORE_HANDLER_REGEX_PATTERN
)


class Module:
    """
    Main class for creating modules
    """

    def __init__(self, *, name: str, description: str, emoji: str):
        """

        :param name: Module name
        :param description: Module description, what module can do
        """
        self.name = name.capitalize()
        self.description = description.capitalize()
        self.emoji = emoji
        self.__functions__: list[ModuleFunction] = []

    @staticmethod
    def _format_command(command: str) -> str:
        if command[0] not in ascii_lowercase:
            raise exceptions.BadCommandError(f"Bad command ({command})")

        return command.strip().lower()

    @staticmethod
    def _format_docstring(docstring: str) -> str:
        return docstring.strip("\n ")

    @staticmethod
    def get_decoration(parse_mode: ParseMode) -> Union[html, markdown]:
        return html if parse_mode is ParseMode.HTML else markdown

    def get_function_obj(self, by_command: str) -> FuncType:
        for function in self.__functions__:
            if function.check_command(to_check=by_command):
                return function.func_obj

    def function(self, /, __command: str):
        # Fake decorator to get arguments.
        """
        Decorator for module functions.

        **Use it to bind the function to the controller.**
        """

        def _actual_decorator(func_obj: FuncType):
            self.__functions__.append(
                ModuleFunction(
                    command=self._format_command(command=__command),
                    description=self._format_docstring(docstring=func_obj.__doc__),
                    func_obj=func_obj
                )
            )

            def wrapper(*args, **kwargs):
                return func_obj(*args, **kwargs)

            return wrapper

        return _actual_decorator


class Dispatcher:
    """
    **Dispatcher for starting userbots**
    """

    def __init__(
            self,
            *,
            session_string: str = "",
            api_id: int,
            api_hash: str,
            command_prefix: Literal["-", "!"] | str,
            parse_mode: ParseMode = ParseMode.HTML,
            register_base_modules: bool = True
    ):
        self._session_string = session_string
        self._api_id = api_id
        self._api_hash = api_hash
        self._command_prefix = command_prefix
        self._parse_mode = parse_mode
        self._register_base_modules = register_base_modules
        self._modules: list[Module] = []
        self._telegram_client: TelegramClient | None = None

        if self._is_bad_prefix():
            raise exceptions.BadPrefixError(
                f"Prefix \"{self.command_prefix}\" is bad. "
                f"See more info at: ...there would be url to docs"  # TODO add docs url
            )

    def _extract_command(self, text: str) -> str:
        return text.removeprefix(self._command_prefix).split()[0]

    @staticmethod
    def _extract_args(text: str) -> CommandArgs:
        return CommandArgs(args=text.split()[1:])

    @staticmethod
    def _extract_text(event: NewMessage) -> str:
        return event.message.message

    def _is_bad_prefix(self) -> bool:
        return self._command_prefix in BAD_PREFIXES

    def _save_session_string(self):
        with open("save.session.string", "w") as file:
            file.write(self._session_string)

    def _make_pattern(self):
        return CORE_HANDLER_REGEX_PATTERN.format(prefix=self._command_prefix)

    def _get_function_obj(self, by_command: str) -> FuncType:
        for module in self._modules:
            func = module.get_function_obj(by_command=by_command)
            if func:
                return func

    @staticmethod
    def _get_args(func_obj: FuncType) -> dict:
        sig_params = inspect.signature(obj=func_obj).parameters
        dict_args = {}
        for key in sig_params:
            dict_args.update({key: None})
        return dict_args

    def _build_kwargs(self, func_obj: FuncType, event: Event, command_args: CommandArgs):
        result = {}
        for key in self._get_args(func_obj=func_obj):
            match key:
                case "event":
                    result.update({key: event})
                case "client":
                    result.update({key: self._telegram_client})
                case "command_args":
                    result.update({key: command_args})
                case "dp":
                    result.update({key: self})
        return result

    @staticmethod
    def _get_base_module(module_name: str) -> ModuleType:
        return importlib.import_module(f"smart_tg.base_modules.{module_name}")

    def _register_module(self, module: Module):
        if module.name[-2:] != MODULE_SHOULD_ENDS_WITH:
            warnings.warn(
                "The module name should better end with \"er\"\n"
                "e.g. \"Deleter\"\n"
                "\n"
                "This is to ensure that module names do not conflict with command names"
            )

        self._modules.append(module)

    def get_modules(self):
        return self._modules

    @property
    def parse_mode(self):
        return self._parse_mode

    @property
    def command_prefix(self):
        return self._command_prefix

    def register_modules(self, modules: list[Module]):
        for module in modules:
            self._register_module(module=module)

    async def start(self):
        if self._session_string:
            self._telegram_client = TelegramClient(
                session=StringSession(string=self._session_string),
                api_id=self._api_id,
                api_hash=self._api_hash
            )
        else:
            self._telegram_client = TelegramClient(
                session=StringSession(),
                api_id=self._api_id,
                api_hash=self._api_hash
            )

        if self._register_base_modules:
            deleter = self._get_base_module(module_name="deleter")
            helper = self._get_base_module(module_name="helper")
            self.register_modules(
                modules=[
                    deleter.module,
                    helper.module
                ]
            )

        await self._telegram_client.start()
        self._session_string = self._telegram_client.session.save()
        self._telegram_client.parse_mode = self._parse_mode.value

        try:
            @self._telegram_client.on(
                event=NewMessage(
                    from_users="me",
                    pattern=self._make_pattern()
                ))
            async def _core_handler(event: Event):
                text = self._extract_text(event=event)
                command = self._extract_command(text=text)
                command_args = self._extract_args(text=text)

                func_obj = self._get_function_obj(by_command=command)
                if not func_obj:
                    return

                await func_obj(**self._build_kwargs(
                    func_obj=func_obj,
                    event=event,
                    command_args=command_args
                ))
                return

            await self._telegram_client.run_until_disconnected()

        except (KeyboardInterrupt, CancelledError):
            self._save_session_string()
            self._telegram_client.disconnect()
            core_logger.error("Unexpected execution break")
            core_logger.info("Session string saved to file \"save.session.string\"")

        except BaseException as exc:
            self._save_session_string()
            self._telegram_client.disconnect()
            core_logger.error(f"Unexpected error: {exc}")
            core_logger.info("Session string saved to file \"save.session.string\"")

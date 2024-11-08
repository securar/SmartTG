from typing import Coroutine, Callable, Literal

from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.sessions import StringSession

from smart_tg import exceptions
from smart_tg.types import Function
from smart_tg.enums import ParseMode
from smart_tg.loggers import core_logger
from smart_tg._constants import BAD_PREFIXES


class Module:
    """
    Main class for creating modules
    """

    def __init__(self, *, name: str, description: str):
        """

        :param name: Module name
        :param description: Module description, what module can do
        """
        self.name = name
        self.description = description
        self.functions: list[Function] = []

    def function(self, command: str, description: str):
        # Fake decorator to get arguments.
        """
        Decorator for module functions.

        **Use it to bind the function to the controller.**

        :param command: Command for usage in telegram **(without prefix)**
        :param description: Description, what function can do
        :return:
        """

        def _actual_decorator(func: Callable[[NewMessage.Event, TelegramClient], Coroutine]):
            self.functions.append(
                Function(
                    command=command,
                    description=description,
                    func=func
                )
            )

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

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
            parse_mode: ParseMode = ParseMode.HTML
    ):
        self._session_string = session_string
        self._api_id = api_id
        self._api_hash = api_hash
        self._command_prefix = command_prefix
        self._modules: list[Module] = []
        self._telegram_client: TelegramClient | None = None
        self._parse_mode = parse_mode

        if self._is_bad_prefix():
            raise exceptions.BadPrefixError(
                f"Prefix \"{self.command_prefix}\" is bad. "
                f"See more info at: ...there would be url to docs"  # TODO add docs url
            )

    @property
    def command_prefix(self):
        return self._command_prefix

    def _extract_command(self, text: str) -> str:
        return text.removeprefix(self._command_prefix)

    def _is_bad_prefix(self) -> bool:
        return self._command_prefix in BAD_PREFIXES

    def register_module(self, module: Module):
        self._modules.append(module)

    def register_modules(self, modules: list[Module]):
        for module in modules:
            self._modules.append(module)

    def _save_session_string(self):
        with open("save.session.string", "w") as file:
            file.write(self._session_string)

    def _build_default_help_message(self, event: NewMessage.Event) -> str:
        ...
        # message_text =

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
        await self._telegram_client.start()
        self._session_string = self._telegram_client.session.save()
        self._telegram_client.parse_mode = self._parse_mode.value
        try:
            @self._telegram_client.on(event=NewMessage(from_users="me", pattern=f"^{self.command_prefix}.+$"))
            async def core_handler(event: NewMessage.Event):
                command = self._extract_command(text=event.message.message)
                for module in self._modules:
                    for function in module.functions:
                        if function.command == command:
                            await function.func(event, self._telegram_client)
                            return

                # Executes only when user has not implemented its own handler for the help command
                if command == "help":
                    await event.original_update.message.edit(
                        text=self._build_default_help_message(event=event)
                    )


            await self._telegram_client.run_until_disconnected()
        except KeyboardInterrupt:
            self._save_session_string()
            core_logger.info("Session string saved to file \"save.session.string\"")
        except BaseException as exc:
            self._save_session_string()
            core_logger.error(f"Unexpected error: {exc}")
            core_logger.info("Session string saved to file \"save.session.string\"")

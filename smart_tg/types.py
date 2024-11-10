from typing import Coroutine, Callable

from pydantic import BaseModel, ConfigDict

from telethon import TelegramClient as Client
from telethon.events import NewMessage as _NewMessage

Event = _NewMessage.Event

FuncType = Callable[[Event, Client, 'CommandArgs', 'Dispatcher'], Coroutine] | Callable


class CommandArgs(BaseModel):
    args: list[str]


class ModuleFunction(BaseModel):
    command: str
    description: str
    func_obj: FuncType

    def check_command(self, to_check: str) -> bool:
        return to_check == self.command

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

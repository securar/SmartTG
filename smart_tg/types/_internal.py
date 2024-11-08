from typing import Coroutine, Callable

from pydantic import BaseModel

from telethon import TelegramClient
from telethon.events import NewMessage


class Function(BaseModel):
    command: str
    description: str
    func: Callable[[NewMessage.Event, TelegramClient], Coroutine]

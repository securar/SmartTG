from telethon import events
from telethon.events import NewMessage

from smart_tg.smarts import SmartClient
from smart_tg.loggers import core_logger
from smart_tg.helpers import extract_text_from_event
from smart_tg.texts import build_help_message

from config import env_settings, MODULES, PREFIX

client = SmartClient(
    session="core",
    api_id=env_settings.API_ID,
    api_hash=env_settings.API_HASH
)
client.parse_mode = "html"
client.register_modules(modules=MODULES)


@client.on(NewMessage(from_users="me"))
async def pre_handler(event: NewMessage.Event):
    text = extract_text_from_event(event=event)
    if text == "-help":
        help_text = build_help_message(modules=MODULES)
        original_msg = event.original_update.message
        await original_msg.edit(
            text=help_text
        )


@client.on(NewMessage(from_users="me"))
async def handle_command(event: NewMessage.Event):
    text = extract_text_from_event(event=event)
    for module in client.modules:
        for func in module.funcs:
            if text == PREFIX + func.command:
                await func.func(event, client)


def start_core_handler():
    client.start()
    core_logger.info("Started")
    client.run_until_disconnected()


if __name__ == '__main__':
    start_core_handler()

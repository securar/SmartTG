from telethon.events import NewMessage


def extract_text_from_event(event: NewMessage.Event):
    return event.original_update.message.message

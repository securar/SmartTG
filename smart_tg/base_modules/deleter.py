import asyncio

from smart_tg import Module, html
from smart_tg.types import Event, Client, CommandArgs
from smart_tg.logger import create_logger

module = Module(
    name="Deleter",
    description="Module for deleting messages",
    emoji="🗑"
)
logger = create_logger("deleter")


def is_service_message(event: Event) -> bool:
    reply_to = event.reply_to
    return reply_to.forum_topic and not reply_to.reply_to_top_id


@module.function("del")
async def delete(event: Event):
    """
    Delete the message in reply to which the command was sent
    """
    if event.is_reply and not is_service_message(event=event):
        reply_message = await event.get_reply_message()
        await event.message.delete()
        await reply_message.delete()
    else:
        await event.message.edit(
            text=html.bold(f"❌ Command should be used in reply to other message")
        )


@module.function("delme")
async def delete(event: Event, client: Client, command_args: CommandArgs):
    """
    Delete user messages
    Usage: delme *amount*
    """
    args = command_args.args
    if args:
        amount = int(args[0])
        tasks = [event.message.delete(), ]
        async for message in client.iter_messages(
                entity=event.message.chat_id,
                limit=amount + 1,
                from_user="me"
        ):
            tasks.append(message.delete())
        await asyncio.gather(*tasks)
    else:
        example = f"delme *amount*"
        await event.message.edit(
            text=html.bold(
                f"❌ Wrong usage\n"
                f"Example: {html.code(example)}"
            )
        )


@module.function("delete_all_messages")
async def delete(event: Event, client: Client, args: CommandArgs):
    """
    Delete ALL user messages in current chat
    Usage: delete_all_messages
    """
    if not args:
        confirmation = html.code("delete_all_messages i_am_sure")
        await event.message.edit(
            text=html.bold(
                f"❗ This command will delete ALL your messages in this chat\n"
                f"\n"
                f"Type \"{confirmation}\" for confirm."
            )
        )
    elif args[0] == "i_am_sure":
        tasks = [event.message.delete(), ]
        async for message in client.iter_messages(
                entity=event.message.chat_id,
                limit=float("inf"),
                from_user="me"
        ):
            tasks.append(message.delete())
        await asyncio.gather(*tasks)

from smart_tg import Module, Dispatcher
from smart_tg.types import Event, CommandArgs
from smart_tg.logger import create_logger
from smart_tg.enums import ParseMode

module = Module(
    name="Helper",
    description="Show help for modules and commands",
    emoji="⛑"
)
logger = create_logger("helper")


def make_module_info_string(name: str, commands: list[str], emoji: str, parse_mode: ParseMode) -> str:
    decoration = module.get_decoration(parse_mode=parse_mode)
    formatted_commands = [decoration.code(command) for command in commands]
    commands_string = f"( {" | ".join(formatted_commands)} )"
    return f"{emoji} {decoration.bold(name)}: {commands_string}\n"


def make_detailed_module_info_string(target_module: Module, parse_mode: ParseMode) -> str:
    decoration = module.get_decoration(parse_mode=parse_mode)
    title = decoration.bold(f"{target_module.emoji} {target_module.name}\n")
    desc = f"{target_module.description}\n\n"
    commands_string = "".join([
        f"{decoration.code(function.command)}: {function.description}\n"
        for function in target_module.__functions__
    ])
    return title + desc + commands_string


@module.function("help")
async def help_(event: Event, dp: Dispatcher, command_args: CommandArgs):
    """
    Shows modules and commands
    Also you can get description of a command:
    help *command* (without prefix)
    """
    args = command_args.args
    if not args:
        info_strings = []
        for module_ in dp.get_modules():
            commands = [function.command for function in module_.__functions__]
            info_strings.append(
                make_module_info_string(
                    name=module_.name,
                    commands=commands,
                    emoji=module_.emoji,
                    parse_mode=dp.parse_mode
                )
            )
        await event.message.edit(
            text="".join(info_strings)
        )
    else:
        decoration = module.get_decoration(parse_mode=dp.parse_mode)
        target_name = args[0].lower()
        for module_ in dp.get_modules():
            text = make_detailed_module_info_string(
                target_module=module_,
                parse_mode=dp.parse_mode
            )
            if module_.name.lower() == target_name:
                await event.message.edit(text=text)
                return
            for function in module_.__functions__:
                if function.command == target_name:
                    await event.message.edit(text=text)
                    return

        await event.message.edit(text=decoration.bold(
            f"❌ Cant find \"{decoration.code(target_name)}\" :("
        ))

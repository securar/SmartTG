from smart_tg.smarts import SmartModule


def build_help_message(modules: list[SmartModule]):
    message = []
    for module in modules:
        first_string = f"<code>{module.name}</code>: <b>{module.description}</b>\n"
        funcs_string = ""
        for func in module.funcs:
            funcs_string += f"<b># Command \"<code>{func.command}</code>\"</b> - {func.description}\n"
        module_string = first_string + funcs_string + "\n"
        message.append(module_string)
    return "".join(message)

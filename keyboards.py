from aiogram import types


def main_menu_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Add message ➕",
                    callback_data=f"add_message_main_menu",
                ),
                types.InlineKeyboardButton(
                    text="Show message list 📄",
                    callback_data=f"show_message_list_main_menu",
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="Get active message 🔍",
                    callback_data=f"get_active_message_main_menu",
                ),

                types.InlineKeyboardButton(
                    text="Set time 🕔",
                    callback_data=f"set_time_main_menu",
                ),
            ],
        ]
    )

    return markup


def message_buttons(pk: int, is_active: bool) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"Set active ☑️" if not is_active else "ACTIVE ✅",
                    callback_data=f"set_active_{pk}",
                ),
                types.InlineKeyboardButton(
                    text="Delete ⛔",
                    callback_data=f"delete_{pk}",
                ),
            ],
        ]
    )

    return markup
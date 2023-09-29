import asyncio
import os

from aiocron import crontab
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database_manager import DBManager
from keyboards import main_menu_markup, message_buttons
from send_messages import MessageSender
from write_comments import CommentWriter

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
router = Router()
db_manager = DBManager()
START_TIME = None
END_TIME = None


class States(StatesGroup):
    add_message_state = State()
    add_time_state = State()


# --------- ⬇️ START ⬇️ ---------
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        text="""Welcome. This bot allows you to setup and manage your auto commenting.""",
        reply_markup=main_menu_markup(),
    )


# --------- ⬇️ ADD MESSAGE ⬇️ ---------
@router.callback_query(F.data == "add_message_main_menu")
async def handle_add_message(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.add_message_state)
    await callback_query.message.answer(text="Send me message to add")


@router.message(States.add_message_state)
async def add_message(message: types.Message, state: FSMContext):
    db_manager.add_message(message=message.text)
    await state.clear()
    await message.answer("Message has added successfully")


# --------- ⬇️ SHOW ALL MESSAGES ⬇️ ---------
@router.callback_query(F.data == "show_message_list_main_menu")
async def handle_show_all_messages(callback_query: types.CallbackQuery):
    all_messages = db_manager.get_all_messages()
    for message in all_messages:
        await callback_query.message.answer(
            text=message[1],
            reply_markup=message_buttons(pk=message[0], is_active=message[2]),
        )


# --------- ⬇️ DELETE ⛔ ⬇️ ---------
@router.callback_query(F.data.startswith("delete"))
async def delete_message(callback_query: types.CallbackQuery):
    pk = int(callback_query.data.split("_")[-1])
    db_manager.delete_message_by_pk(pk=pk)
    await callback_query.message.delete()


# --------- ⬇️ SET ACTIVE  ☑️ ⬇️ ---------
@router.callback_query(F.data.startswith("set_active"))
async def delete_message(callback_query: types.CallbackQuery):
    pk = int(callback_query.data.split("_")[-1])
    db_manager.set_active_message(message_pk=pk)
    await callback_query.message.answer(text="🔄 UPDATED 🔄")
    await handle_show_all_messages(callback_query=callback_query)


# --------- ⬇️ GET ACTIVE MESSAGE ⬇️ ---------
@router.callback_query(F.data == "get_active_message_main_menu")
async def get_active_message(callback_query: types.CallbackQuery):
    active_message = db_manager.get_active_message_text()
    await callback_query.message.answer(text=active_message)


# --------- ⬇️ SEND MESSAGES ⬇️ ---------
@router.message(Command("send_messages"))
async def send_messages(message: types.Message):
    sender = MessageSender()
    await START_TIME.next()
    await message.answer(text="Messages have started to send")
    await sender.run()
    await END_TIME.next()


# --------- ⬇️ WRITE COMMENTS ⬇️ ---------
@router.message(Command("write_commentaries"))
async def test(message: types.Message):
    writer = CommentWriter()
    await START_TIME.next()
    await message.answer(text="comments have started to post")
    await writer.run()
    await END_TIME.next()


# --------- ⬇️ SET TIME ⬇️ ---------
@router.callback_query(F.data == "set_time_main_menu")
async def set_time(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.add_time_state)
    await callback_query.message.answer(text="Send me time in format: 18:00 to 20:00")


@router.message(States.add_time_state)
async def add_message(message: types.Message, state: FSMContext):
    try:
        start_time, end_time = message.text.split(" to ")
        start_time_hours, start_time_minutes = map(int, start_time.split(":"))
        end_time_hours, end_time_minutes = map(int, end_time.split(":"))

        if (
            0 <= start_time_hours <= 23
            and 0 <= start_time_minutes <= 59
            and 0 <= end_time_hours <= 23
            and 0 <= end_time_minutes <= 59
        ):
            global START_TIME, END_TIME
            START_TIME = crontab(f"{start_time_minutes} {start_time_hours} * * *")
            END_TIME = crontab(f"{end_time_minutes} {end_time_hours} * * *")
            await message.answer("Time has set")

    except ValueError:
        await message.answer(text="Incorrect time format")
    finally:
        await state.clear()


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

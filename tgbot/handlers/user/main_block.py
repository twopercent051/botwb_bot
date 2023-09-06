from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.models.redis_connector import RedisConnector

router = Router()


@router.message(Command("start"))
async def main_block(message: Message):
    user_id = int(message.from_user.id)
    sticker_id = "CAACAgIAAxkBAAEJ4wtkyiACnd7MiPbDj0pnvHCXOb2MCAACAQEAAladvQoivp8OuMLmNC8E"  # Замените на ID нужного вам стикера
    await message.answer_sticker(sticker_id)
    current_users = RedisConnector.get_redis(redis_db="users")
    if user_id not in current_users:# отправка сообщения что юзер запустил бота
        RedisConnector.append_redis(redis_db="users", value=user_id)
        await bot.send_message(436290347, f'user {message.from_user.id} запустил бота')

    user_channel_status = await bot.get_chat_member(chat_id, message.from_user.id)# проверка на наличия пользователя в группе
    if user_channel_status["status"] == 'left':
        await bot.send_message(message.from_user.id, 'Подпишитесь на канал https://t.me/+6dRLrSfmefhhODRi чтобы использовать бота', reply_markup=inline_kb)
        return

    welcome_message = "Здравствуйте! Напишите ключевое слово, а я вам ставки на автоматизированную рекламу! 💼"
    await message.reply(welcome_message)

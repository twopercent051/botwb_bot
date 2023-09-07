from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from create_bot import bot, config
from tgbot.handlers.user.inline import InlineKeyboard
from tgbot.handlers.user.middlewares import BlockUserMiddleware
from tgbot.misc.states import UserFSM
from tgbot.models.redis_connector import RedisConnector
from tgbot.services.get_products import Products

router = Router()
router.message.outer_middleware(BlockUserMiddleware())
router.callback_query.outer_middleware(BlockUserMiddleware())

inline = InlineKeyboard()

admins = config.tg_bot.admin_ids


async def welcome_render(user_id: str | int):
    text = "Для выбора функционала нажмите на кнопку меню (слева внизу)"
    await bot.send_message(chat_id=user_id, text=text)


@router.message(Command("start"))
@router.message(Command("menu"))
async def main_block(message: Message):
    user_id = int(message.from_user.id)
    sticker_id = "CAACAgIAAxkBAAEJ4wtkyiACnd7MiPbDj0pnvHCXOb2MCAACAQEAAladvQoivp8OuMLmNC8E"
    await message.answer_sticker(sticker_id)
    current_users = RedisConnector.get_redis(redis_db="users")
    if user_id not in current_users:
        RedisConnector.append_redis(redis_db="users", value=user_id)
        for admin in admins:
            text = f"Пользователь {hcode(user_id)} запустил бота"
            await bot.send_message(chat_id=admin, text=text)
    await welcome_render(user_id=user_id)


@router.callback_query(F.data == "check")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserFSM.get_kw)
    await welcome_render(user_id=callback.from_user.id)
    await bot.answer_callback_query(callback.id)


@router.message(Command("auto"))
async def main_block(message: Message, state: FSMContext):
    text = "Здравствуйте! Напишите ключевое слово, а я вам ставки на автоматизированную рекламу! 💼"
    await state.set_state(UserFSM.get_kw)
    await message.answer(text)


@router.message(Command("spp"))
async def main_block(message: Message, state: FSMContext):
    text = "Привет! Введите артикул товара, чтобы получить информацию о скидке."
    await state.set_state(UserFSM.get_article)
    await message.answer(text)


@router.message(F.text, UserFSM.get_kw)
async def main_block(message: Message):
    keyword = message.text.strip()
    result_chunk = Products.product_info_render(keyword=keyword)
    for chunk in result_chunk:
        await message.answer("\n".join(chunk))


@router.message(F.text, UserFSM.get_article)
async def main_block(message: Message):
    product = Products.discount_info_render(article=message.text.strip())
    if product[0] == 200:
        kb = inline.item_subscribe_kb(article=message.text.strip())
        await message.answer(product[1], reply_markup=kb)
        text = "Для продолжения работы, введите следующий артикул."
    else:
        text = "Что-то пошло не так 🤷"
        for admin in admins:
            await bot.send_message(chat_id=admin, text=product[1])
    await message.answer(text)


@router.callback_query(F.data.split(":")[0] == "subscribe")
async def main_block(callback: CallbackQuery):
    article = callback.data.split(":")[1]
    product = Products.get_discount(article=article)
    product_data = dict(article=article, user_id=callback.from_user.id, price=product[1]['salePriceU'] / 100)
    RedisConnector.append_redis(redis_db="products", value=product_data)
    await callback.message.answer(f"{article} добавлен")
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "subscribe_off")
async def main_block(callback: CallbackQuery):
    article = callback.data.split(":")[1]
    RedisConnector.delete_product(article=article)
    text = f"Товар {article} больше не отслеживается"
    await callback.message.answer(text)
    await bot.answer_callback_query(callback.id)

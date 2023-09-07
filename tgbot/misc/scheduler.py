from create_bot import config, scheduler, bot
from tgbot.handlers.user.inline import InlineKeyboard
from tgbot.models.redis_connector import RedisConnector
from tgbot.services.get_products import Products

admins = config.tg_bot.admin_ids

inline = InlineKeyboard()


class Scheduler:

    @staticmethod
    async def check_price():
        products = RedisConnector.get_redis(redis_db="products")
        for product in products:
            discount_data = Products.get_discount(article=product["article"])
            if discount_data[0] == 200:
                if discount_data[1]:
                    diff = int(product["price"]) - int(discount_data[1]["salePriceU"] / 100)
                    if diff > 0:
                        word = "УМЕНЬШИЛАСЬ"
                    elif diff < 0:
                        word = "УВЕЛИЧИЛАСЬ"
                    else:
                        continue
                    text = f"ИЗМЕНЕНИЕ ЦЕНЫ!\nЦЕНА {word} НА {abs(diff)} рублей"
                    product_info = Products.discount_info_render(article=product["article"], old_price=product["price"])[1]
                    text = f"{text}\n{product_info}"
                    kb = inline.item_subscribe_off_kb(article=product["article"])
                    await bot.send_message(chat_id=product["user_id"], text=text, reply_markup=kb)
                    RedisConnector.delete_product(article=product["article"])
                    product_data = dict(article=product["article"],
                                        user_id=product["user_id"],
                                        price=int(discount_data[1]["salePriceU"] / 100))
                    RedisConnector.append_redis(redis_db="products", value=product_data)
                else:
                    RedisConnector.delete_product(article=product["article"])
            else:
                for admin in admins:
                    await bot.send_message(chat_id=admin, text=product[1])
                break

    @classmethod
    def tasker(cls):
        scheduler.add_job(func=cls.check_price,
                          trigger="interval",
                          minutes=1,
                          misfire_grace_time=None)

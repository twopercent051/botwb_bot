import itertools
from typing import List, Optional

import requests


class Products:

    @staticmethod
    def __paginator(item_list: list, size: int) -> List[tuple]:
        it = iter(item_list)
        return iter(lambda: tuple(itertools.islice(it, size)), ())

    @staticmethod
    def __get_products_by_keyword(keyword):
        url = f"https://search.wb.ru/exactmatch/ru/male/v4/search"
        params = {
            "TestGroup": "control",
            "TestID": 155,
            "appType": 1,
            "curr": "rub",
            "dest": -445281,
            "query": keyword,
            "regions": "80,38,83,4,64,33,68,70,30,40,86,75,69,22,1,31,66,110,48,71,114",
            "resultset": "catalog",
            "sort": "popular",
            "spp": 29,
            "suppressSpellcheck": "false",
            "uclusters": 2
        }
        response = requests.get(url, params=params)
        data = response.json()
        filtered_products = []
        if "data" in data and "products" in data["data"]:
            products = data["data"]["products"]
            filtered_products = []
            for p in products:
                if "log" in p and "promotion" in p["log"] and p["log"]["promotion"] == 1:
                    filtered_products.append(p)
        return filtered_products

    @classmethod
    def product_info_render(cls, keyword: str, chunk_size: int = 50):
        products = cls.__get_products_by_keyword(keyword=keyword)
        result = []
        for product in products:
            text = [
                f"🔍 {product['log']['cpm']} ₽",
                str(product["id"]),
                str(keyword),
                f"Промо - позиция: {product['log']['promoPosition']}",
                f"Позиция: {product['log']['position']}"
            ]
            result.append(" | ".join(text))
        result_chunks = cls.__paginator(item_list=result, size=chunk_size)
        return result_chunks

    @staticmethod
    def get_discount(article: str) -> Optional[tuple]:
        url = f"https://card.wb.ru/cards/detail?appType=1&curr=rub&spp=25&nm={article}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if len(data["data"]["products"]) > 0:
                return response.status_code, data["data"]["products"][0]
            else:
                return response.status_code, None
        else:
            return response.status_code, None

    @classmethod
    def discount_info_render(cls, article: str, old_price: Optional[float] = 0) -> str:
        product = cls.get_discount(article=article)
        status = product[0]
        if status != 200:
            text = f"При парсинге {article} словили статус {product[0]}"
        else:
            if product[1]:
                text = [
                    f"СПП по Артикулу {article}\n",
                    f"- Артикул товара: {product[1]['id']}",
                    f"- Название товара: {product[1]['name']}",
                    f"- Бренд: {product[1]['brand']}", ]
                if old_price != 0:
                    text.append(f"- Старая цена: {old_price} р")
                text.extend([
                    f"- Цена со скидкой: {product[1]['extended']['basicPriceU'] / 100} р",
                    f"- Цена для клиента: {product[1]['salePriceU'] / 100} р",
                    f"- Скидка СПП: {product[1]['extended']['clientSale']} %"
                ])
                text = "\n".join(text)
            else:
                text = "Товар с таким артикулом не найден."
        return status, text


if __name__ == "__main__":
    a = Products.get_discount("171946125fff")
    print(a)

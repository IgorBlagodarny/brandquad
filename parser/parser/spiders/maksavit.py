import re
from datetime import datetime

import scrapy
from constans.maksavit import *
from scrapy import Request, Selector
from w3lib.url import url_query_parameter, add_or_replace_parameter

class MaksavitHandler:
    def get_product(self, product):
        result = {
        "timestamp": int(datetime.now().timestamp()),  # Дата и время сбора товара в формате timestamp.
        "RPC": str(product.get('id')),  # Уникальный код товара.
        "url": f"https://maksavit.ru/catalog/{product.get('urlId')}/",  # Ссылка на страницу товара.
        "title": product.get('name', ''),  # Заголовок/название товара (! Если в карточке товара указан цвет или объем, но их нет в названии, необходимо добавить их в title в формате: "{Название}, {Цвет или Объем}").
        "marketing_tags": [],  # Список маркетинговых тэгов, например: ['Популярный', 'Акция', 'Подарок']. Если тэг представлен в виде изображения собирать его не нужно.
        "brand": product.get('brandString', ''),  # Бренд товара.
        "section": [breadcrumb['name'] for breadcrumb in product.get('category', [])],  # Иерархия разделов, например: ['Игрушки', 'Развивающие и интерактивные игрушки', 'Интерактивные игрушки'].
        "price_data": {
            "current": .0,  # Цена со скидкой, если скидки нет то = original.
            "original": .0,  # Оригинальная цена.
            "sale_tag": '',  # Если есть скидка на товар то необходимо вычислить процент скидки и записать формате: "Скидка {discount_percentage}%".
        },
        "stock": {
            "in_stock": product.get('active', True),  # Есть товар в наличии в магазине или нет.
            "count": product.get('availableOfferCount', 0)  # Если есть возможность получить информацию о количестве оставшегося товара в наличии, иначе 0.
        },
        "assets": {
            "main_image": '',  # Ссылка на основное изображение товара.
            "set_images": [],  # Список ссылок на все изображения товара.
            "view360": [],  # Список ссылок на изображения в формате 360.
            "video": []  # Список ссылок на видео/видеообложки товара.
            },
            "metadata": {
                "__description": "",  # Описание товара
                # Также в metadata необходимо добавить все характеристики товара которые могут быть на странице.
                # Например: Артикул, Код товара, Цвет, Объем, Страна производитель и т.д.
                # Где KEY - наименование характеристики.
            },
            "variants": 0,  # Кол-во вариантов у товара в карточке (За вариант считать только цвет или объем/масса. Размер у одежды или обуви варинтами не считаются).
        }
        if type(product['picture']) == str:
            result['assets']['main_image'] = product['picture']
            result['assets']['set_images'] = [product['picture']]
        elif type(product['picture']) == list:
            result['assets']['main_image'] = product['picture'][0]
            result['assets']['set_images'] = product['picture']
        if not result['assets']['main_image'].startswith("http"):
            result['assets']['main_image'] = f"{DOMAIN}{result['assets']['main_image']}"

        for i in range(len(result['assets']['set_images'])):
            if not result['assets']['set_images'][i].startswith('http'):
                result['assets']['set_images'][i] = f"{DOMAIN}{result['assets']['set_images'][i]}"

        if result['stock']['in_stock']:
            prices = [price for price in [product.get('pastPrice', .0), product.get('price', .0)] if price > 0]
            result['price_data']['current'] = min(prices)
            result['price_data']['original'] = max(prices)
            try:
                result['price_data']['sale_tag'] = f"Скидка {round((1 - result['price_data']['current']/result['price_data']['original'])*100, 2)}%"
            except:
                self.logger.info(f"Не удалось посчитать цену для {result['price_data']['current']}/{result['price_data']['original']}")

        return result

    def get_metadata(self, response):
        metadata = {
                "__description": "",
            }
        paragraphs = [Selector(text=paragraph) for paragraph in response.xpath(METADATA_PARAGRAPH).getall()]
        for paragraph in paragraphs:
            key = paragraph.xpath(METADATA_KEY).get()
            if key:
                value = ' '.join(paragraph.xpath(METADATA_CONTENT).getall())
                if key.lower() == 'описание':
                    metadata['__description'] = value
                else:
                    if value:
                        metadata[key.strip()] = value
        return metadata

    def get_product_urls(self, response):
        products_slugs = response.xpath(PRODUCT_URLS).getall()
        product_urls = [f"{DOMAIN}{slug}" for slug in products_slugs]
        return product_urls
    def get_slug_from_url(self, url):
        slug = re.search("https://maksavit\.ru/(?P<location>\w+(-\w+)*)(?P<slug>.+)\??", url).group('slug')
        return slug


class MaksavitSpider(scrapy.Spider, MaksavitHandler):
    name = "maksavit"
    allowed_domains = ["maksavit.ru"]
    start_urls = START_URLS

    def start_requests(self):
        for url in self.start_urls:
            category_slug = self.get_slug_from_url(url)
            api_url = CATEGORY_API.format(slug=category_slug, page=1)
            yield Request(api_url, callback=self.parse, cookies=COOKIES, headers=CATEGORY_HEADERS)

    def parse(self, response):
        data = response.json()

        if products := data['products']:
            for product in products:
                product = self.get_product(product)
                yield Request(product['url'], callback=self.parse_product, cookies=COOKIES, meta={'product': product})

            if len(products) == 15:
                page = int(url_query_parameter(response.url, 'page'))
                yield Request(add_or_replace_parameter(response.url, 'page', page+1), callback=self.parse, cookies=COOKIES, headers=CATEGORY_HEADERS)

        else:
            self.logger.info(f"LAST PAGE FROM {response.url}")

    def parse_product(self, response):
        product = response.meta['product']
        product['variants'] = len(response.xpath(VARIANTS_COUNT).getall())
        product['metadata'] = self.get_metadata(response)
        yield product
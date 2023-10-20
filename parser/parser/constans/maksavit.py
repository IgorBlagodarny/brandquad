
START_URLS = [
    # "https://maksavit.ru/catalog/4774/",
    'https://maksavit.ru/novosibirsk/catalog/flebologiya/venotoniki_vnutr/',
    # 'https://maksavit.ru/velikij-novgorod/catalog/vitaminy/'
]

CATEGORY_API = "https://maksavit.ru/api{slug}?analogsSummary=1&hideFilter=1&page={page}"
CATEGORY_HEADERS = headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://maksavit.ru/novosibirsk/catalog/flebologiya/venotoniki_vnutr/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 OPR/103.0.0.0 (Edition Yx 05)',
    'X-Requested-With': 'XMLHttpRequest',
}
COOKIES = {'location_code': '0000949228'}
DOMAIN = "https://maksavit.ru"

# ==============CONSTANTS XPATH===============
PRODUCT_URLS = "//div[contains(@class, 'grid-type-container')]/div[contains(@class, 'product-card-block')]//a[contains(@class, 'preview-img-wrapper')]/@href"
VARIANTS_COUNT = "//div[contains(@class, 'quantity-items-wrapper')]/div"
METADATA_PARAGRAPH = "//div[contains(@class, 'product-instruction__guide')]/div"
METADATA_KEY = "//h3/text()"
METADATA_CONTENT = "//h3/following-sibling::*//text() | //h3/ancestor::div/text()"
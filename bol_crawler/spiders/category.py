from scrapy import Request
from .base import _BaseSpider, Product
import logging
logging.getLogger('scrapy').propagate = False


class CategorySpider(_BaseSpider):
    name = 'categorySpider'

    def _parse_url(self, response):
        paginate = response.meta['paginate']
        try:
            products = response.meta['products']
        except KeyError:
            products = []

        products_found = response.xpath("//li[contains(@class, 'product-item--column')]")
        logging.debug("{} products found on {}".format(len(products_found), response.url))

        for product in products_found:
            products.append(self._parse_product(product))

        if paginate > 0:
            paginate -= 1
            yield from self._crawl_next_page(response, paginate, products)
        else:
            identifier = response.meta['identifier']
            logging.debug("Saved {} products for {}".format(len(products), identifier))
            self._results[identifier] = products

    def _crawl_next_page(self, response, paginate:int, products:list):
        """If there still is a next page, this function sends a request to that url and gives it back to _parse_url"""
        next_page_url = response.xpath(
            "//span[@class='sb sb-chevron-next']/parent::a[not(contains(@href, 'javascript'))]/@href").get()
        if next_page_url:
            logging.debug("Go to the next page on {}".format(response.url))
            yield response.follow(next_page_url, callback=self._parse_url, meta={
                "paginate": paginate,
                "products": products,
                "identifier": response.meta['identifier']
            })
        else:
            self._results[response.meta['identifier']] = products

    def _parse_review_data(self, selector):
        """Parses the selector for a single product to get the review count and average review"""
        try:
            processed_string = ''
            prev_char = 'not_going_to_match'
            for char in selector.xpath("div[2]/descendant-or-self::div[contains(@title, 'sterren')]/@title").get():
                if char.isnumeric() or char == ' ' or char == '.' or char == ',' and prev_char != ' ':
                    processed_string += char
                    prev_char = char

            average_review = processed_string.strip().split(' ')[0]
            review_count = int(selector.xpath(
                "div[2]/descendant-or-self::div[contains(@title, 'sterren')]/@data-count").get())
        except TypeError:
            average_review = review_count = None
        return average_review, review_count

    def _parse_price_data(self, selector):
        """Parses the selector for a single product to get the original and current price"""
        try:
            full_current_price = selector.xpath("div[2]/descendant-or-self::meta[@itemprop='price']/@content").get()
            current_price = float(full_current_price.replace(',', '')) / 100
            original_price = selector.xpath("div[2]/descendant-or-self::del[@data-test='from-price']/text()").get()
            if original_price:
                original_price = float(original_price.replace(',', '')) / 100
            else:
                original_price = current_price
        except AttributeError:  # not in stock
            current_price = -1
            original_price = -1

        return original_price, current_price

    def _parse_product(self, product_html):
        """Parses the selector for a single product to fill in the complete Product class."""
        product = Product()
        product.url = product_html.xpath('a/@href').get()
        product.images.append(product_html.xpath("div/a/img/@src").get())
        product.category = product_html.xpath("div[2]/ul/li/a/text()").get()
        product.title = product_html.xpath("div[2]/a/span/text()").get()

        original_price, current_price = self._parse_price_data(product_html)
        product.original_price = original_price
        product.current_price = current_price

        average_review, review_count = self._parse_review_data(product_html)
        product.average_review = average_review
        product.review_count = review_count

        product.select_delivery = bool(product_html.xpath("div[2]/descendant-or-self::strong[text()='Select']").get())
        product.sold_by = product_html.xpath("div[2]/descendant-or-self::div/a[contains(@class,'product-seller__name')]/text()").get() or 'bol.com'
        product.brand = product_html.xpath("div[2]/descendant-or-self::a[@data-test='party-link']/text()").get()
        return product

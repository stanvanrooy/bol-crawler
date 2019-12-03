from .base import _BaseSpider, Product
import logging
logging.getLogger('scrapy').propagate = False


class ProductSpider(_BaseSpider):
    name = 'productSpider'

    def _parse_url(self, response):
        product = Product()
        product.url = response.url
        product.category = response.xpath("//span[@class='breadcrumbs__link-label']/text()").getall()[-1]
        product.title = response.xpath("//span[@data-test='title']/text()").get()
        product.brand = response.xpath("//a[@data-role='BRAND']/text()").get()
        product.average_review = float(response.xpath("//div[@class='rating-stars']/span/span/span[1]/text()").get())
        product.review_count = int(response.xpath("//div[@class='rating-stars']/following-sibling::span/text()").get())
        product.current_price = response.xpath("//span[@data-test='price']/text()").get().replace(",", ".")
        product.original_price = (response.xpath("//del[@data-test='list-price']/text()").get() or product.current_price).replace(",", ".")
        product.current_price = float(product.current_price)
        product.original_price = float(product.original_price)
        product.sold_by = response.xpath("//a[@class='js_buy_block_seller_popup']/text()").get() or 'bol.com'
        product.description = response.xpath("//div[@data-test='description']/p/descendant-or-self::text()").getall()
        product.images = [x.replace('/thumb/', '/large/') for x in response.xpath("//ul/li/img/@src").getall()]
        product.select_delivery = bool(response.xpath("//div[@class='buy-block']//strong[@data-test='select-logo']").get())
        self._results[response.meta['identifier']] = product
        logging.debug("Crawled {}".format(response.url))

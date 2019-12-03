from scrapy.crawler import CrawlerProcess
from threading import Thread
from bol_crawler.spiders.category import CategorySpider
from bol_crawler.spiders.product import ProductSpider
from uuid import uuid4
import logging


class Crawler:
    """The crawler class is the entry point to access the scraper. The Crawler class handles the queue, processes the
    input and gives it back.
    Args:
        debug(bool)(optional): if set to True, debug messages will be shown
    Attributes:
        category_spider(CategorySpider): holds the CategorySpider instance
        product_spider(ProductSpider):  holds the ProductSpider instance
    """
    def __init__(self, debug=None):
        process = CrawlerProcess()
        process.crawl(CategorySpider)
        process.crawl(ProductSpider)
        self.category_spider = [x.spider for x in process.crawlers if x.spider.name == 'categorySpider'][0]
        self.product_spider = [x.spider for x in process.crawlers if x.spider.name == 'productSpider'][0]
        Thread(target=process.start).start()

        self._configure_logging(debug)

    def _configure_logging(self, debug):
        """Configures logging. """
        logging.getLogger().setLevel(logging.DEBUG if debug else logging.CRITICAL)

    def crawl_products(self, urls:list):
        """Retrieves information about the each product url you specify
        Args:
            urls(list): a list of product urls you want to crawl
        Returns(list):
            a list which contains a spiders.base.Product instance for every product url you entered
        """
        identifiers = []
        products = []
        for url in urls:
            identifier = uuid4()
            identifiers.append(identifier)
            self.product_spider.add_to_queue(url, identifier)

        while len(products) != len(identifiers):
            for identifier in identifiers:
                result = self.product_spider.get_result(identifier)
                if result:
                    products.append(result)

        return products

    def crawl_category(self, url:str, paginate:int):
        """
        Args:
            url: the category url which needs to be crawler
            paginate: how often you want to go to the next page. if you only want to crawl the first page, set this to 0
        Returns(list):
            a list which contains a spider.base.Product instance for every product found on the category pages
        """
        identifier = uuid4()
        url = url + "?view=tile"  # ensure we always get the tile view, we can't process list views.
        self.category_spider.add_to_queue(url, identifier, paginate)

        while True:
            result = self.category_spider.get_result(identifier)
            if result:
                return result

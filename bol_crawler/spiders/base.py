from scrapy import Spider, signals, Request
from scrapy.exceptions import DontCloseSpider


class _BaseSpider(Spider):
    """This class implements the queing system. Each spider inherits from this class, the subclassed classes need to implement
    the _parse_url function to parse the provided urls. This class prevents the spider from closing when there are no more
    requests in the queue, which is the normal behaviour of Scrapy.
    """
    name = 'basespider'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = []
        self._results = {}

    def add_to_queue(self, item:str, identifier:str, paginate:int=None):
        if not paginate: paginate = 0
        self._queue.append({"url": item, "identifier": identifier, "paginate": paginate})

    def get_result(self, identifier:str):
        """This function is used for retrieving processed items with the unique identifier. Returns none if the process
        is not done yet."""
        try:
            return self._results.pop(identifier)
        except KeyError:
            return None

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(_BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.crawler.signals.connect(spider._spider_idle, signal=signals.spider_idle)
        return spider

    def _spider_idle(self):
        self._schedule_next_request()
        raise DontCloseSpider()

    def _schedule_next_request(self):
        req = self._get_next_request()
        if req:
            self.crawler.engine.crawl(req, spider=self)

    def _get_next_request(self):
        """Creates a Request object from the data specified in the dictionaries that are stored in self._queue"""
        if self._queue:
            item = self._queue.pop(0)
            request = Request(
                        item.get('url'),
                        meta={
                            'paginate': item.get('paginate'),
                            'identifier': item.get('identifier')
                        },
                        callback=self._parse_url
                      )

            return request

    def _parse_url(self, response):
        raise NotImplementedError("_crawl_url need to be overwritten")


class Product:
    """Class used for storing product data.

    Attributes:
        url(str): the url where the product can be found
        category(str); the category where the product can be found
        title(str): the product title
        brand(str): the brand name of the product
        review_count(int): amount of reviews
        """
    def __init__(self):
        self.url = str()  # the url where the product can be found
        self.category = str()  # the category in which the product is stored
        self.title = str()  # the product title
        self.brand = str()  # the brand name of the product
        self.review_count = int()  # the amount of reviews
        self.average_review = float()  # the average review
        self.current_price = float()  # the price for which the product is listed right now
        self.original_price = float()  # the original price, this will be different from current_price if there is a discount
        self.sold_by = str()  # either the name of a partnershop or just 'bol.com'
        self.description = list()  # the description split up by newlines
        self.images = list()  # a list containing all image urls
        self.select_delivery = bool()  # True if select delivery is available, otherwise False

    @property
    def discount(self):
        return self.original_price - self.current_price

    def to_dict(self):
        return {
            "url": self.url,
            "category": self.category,
            "title": self.title,
            "brand": self.brand,
            "review_count": self.review_count,
            "average_review": self.average_review,
            "original_price": self.original_price,
            "current_price": self.current_price,
            "discount": self.discount,
            "sold_by": self.sold_by,
            "description": self.description,
            "images": self.images,
            "select_delivery": self.select_delivery
        }

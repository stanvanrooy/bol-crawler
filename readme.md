# bolcom_crawler
[![Downloads](https://pepy.tech/badge/bol-crawler)](https://pepy.tech/project/bol-crawler)
[![PyPI license](https://img.shields.io/pypi/l/instauto)](https://pypi.python.org/project/instauto/)

This is a crawler that makes use of Scrapy to crawl [bol.com](https://bol.com). It can be downloaded as a Python package from PyPi. 

## Usage
The `Crawler` instance has two functions you can use, `crawl_products` and `crawl_category`. See an example below.

```python
from bol_crawler.crawler import Crawler
crawler = Crawler()

# to crawl products
products = crawler.crawl_products(
    [
        'https://www.bol.com/nl/p/lg-34gl750-b-ultragear-gaming-monitor/9200000115819731',
    ]
)

# to crawl a category
products = crawler.crawl_category(
    [
        'https://www.bol.com/nl/l/gaming-toetsenborden/N/18214/', 0  # the 0 value is how often you want to paginate. 0 is just crawling the first page
    ]
)
```

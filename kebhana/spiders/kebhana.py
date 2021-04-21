import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from kebhana.items import Article


class kebhanaSpider(scrapy.Spider):
    name = 'kebhana'
    start_urls = ['https://www.kebhana.com/cont/news/news01/index.jsp']

    def parse(self, response):
        articles = response.xpath('//ul[@class="news_list"]/li')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('./span[@class="date"]/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//div[@class="paging"]//a/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h4/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="tableWrap"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

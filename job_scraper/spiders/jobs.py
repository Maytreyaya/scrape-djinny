import scrapy
from scrapy.http import Response


class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["djinni.co"]

    def start_requests(self):
        urls = [
            "https://djinni.co/jobs/?primary_keyword=Python&exp_level=1y",
            "https://djinni.co/jobs/?primary_keyword=Python&exp_level=2y",
            "https://djinni.co/jobs/?primary_keyword=Python&exp_level=3y",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    #
    # def start_requests(self):
    #     yield scrapy.Request(
    #         url="https://djinni.co/jobs/?primary_keyword=Python",
    #         callback=self.parse)
    #     yield scrapy.Request(
    #         url="https://djinni.co/jobs/?primary_keyword=Python&exp_level=1y",
    #         callback=self.parse)
    #     yield scrapy.Request(
    #         url="https://djinni.co/jobs/?primary_keyword=Python&exp_level=2y",
    #         callback=self.parse)
    #     yield scrapy.Request(
    #         url="https://djinni.co/jobs/?primary_keyword=Python&exp_level=3y",
    #         callback=self.parse)

    def parse(self, response, **kwargs):
        for job_url in response.css("a.profile::attr(href)").getall():
            yield response.follow(job_url, callback=self.parse_job)

        next_page_url = response.css("li.page-item[aria-current='page'] + li.page-item a.page-link::attr(href)").get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    @staticmethod
    def parse_job(response: Response) -> dict:
        technologies = response.css(
            "div.job-additional-info--item-text span:not(.location-text)[class='']::text"
        ).getall()
        yield {
            "title": response.css("h1::text").get().strip(),
            "company": response.css(".job-details--title::text").get().strip(),
            "salary": response.css(".public-salary-item::text").get(),
            "technologies": [span.strip() for span in technologies],
            "location":  response.css(".location-text::text").get().strip(),
        }

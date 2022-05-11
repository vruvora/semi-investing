import scrapy
from bs4 import BeautifulSoup
from itertools import product
from indeed.items import IndeedItem

job_titles = ["GPU", "Embedded%20Engineer", "fabrication%20engineer", "fabrication", "computer architecture"]
country = ["United%20States"]
urls = []
for (job_title, country) in product(job_titles, country):
    url = f"https://www.indeed.com/jobs?q={'-'.join(job_title.split())}&l={country}"
    print(url)
    urls.append(url)



class IndeedSpider(scrapy.Spider):
    name = "indeed"
    allowed_domains = ["indeed.com"]
    start_urls = urls

    def parse_jd(self, response, **posting):
        soup = BeautifulSoup(response.text, features="lxml")
        jd = soup.find("div", {"id": "jobDescriptionText"}).get_text()
        url = response.url
        posting.update({"job_description": jd, "url": url})
        yield posting

    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        # //a[contains(@class,'jcs-JobTitle')]
        # //div[contains(@class, 'companyLocation')]
        #
        locations = soup.find_all('div', attrs={'class': 'companyLocation'})
        for location in locations:
            location = location.get_text()
            item = IndeedItem()
            item['location'] = location
            yield item
        try:
            next_page = soup.find("a", {"aria-label":  "Next"}).get("href")
        except AttributeError:
            next_page = None
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
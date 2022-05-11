# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IndeedItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # job_title = listing.find("h2", {"class": "jobTitle"}).get_text().strip()
            # summary = listing.find("div", {"class": "job-snippet"}).get_text().strip()    # strip newlines
            # company = listing.find("span", {"class": "companyName"}).get_text().strip()
            # location = listing.find("div", {"class": "companyLocation"}).get_text().strip()
    job_title = scrapy.Field()
    summary = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()

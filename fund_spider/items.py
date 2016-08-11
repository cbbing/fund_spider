# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FundSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    uuid = scrapy.Field()
    fund_id = scrapy.Field()
    fund_name = scrapy.Field()
    fund_full_name = scrapy.Field()
    open_date = scrapy.Field()
    nav = scrapy.Field()
    added_nav  = scrapy.Field()
    foundation_date = scrapy.Field()
    statistic_date = scrapy.Field()
    entry_time = scrapy.Field()
    source_code = scrapy.Field()
    source = scrapy.Field()
    org_id = scrapy.Field()

    def __unicode__(self):
        return self.fund_name+","+self.foundation_date

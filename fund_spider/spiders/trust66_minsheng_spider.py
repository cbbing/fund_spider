# -*- coding: utf-8 -*-
"""
中国民生信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import re,json
import hashlib
from scrapy.http import FormRequest
from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
class TrustSxxtSpider(scrapy.Spider):
    name = "trust66_spider"
    allowed_domains = ["msxt.com"]

    start_urls = (
        'http://www.msxt.com/?jzgb.html',
    )


    def parse(self, response):
        self.log(response.url)
        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find('div', {"class":"ims_pager"})
        t = trs.text
        ts=json.loads(t)["last_page"]
        for i in range(1,ts+1):
            url = "http://www.msxt.com/?jzgb/page/%d.html"%i

            yield scrapy.Request(url, callback=self.parse_two)

    def parse_two(self,response):
        self.log(response.url)
        # 请求第一页

        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('td')
        for tr in trs:
            urls = tr.find("div")
            if urls:
                item = FundSpiderItem()
                urll= "http://www.msxt.com" + urls.a['href']

                item['foundation_date'] = tr.next_sibling.next_sibling.text
                item['open_date'] = tr.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.text
                if item['open_date'] == '无':
                    item['open_date'] = None
                print item
                # yield item
                yield scrapy.Request(urll, callback=lambda response, item=item : self.parse_history_nav(response, item))



    def parse_history_nav(self, response,itemTop):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        # html = requests.get(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if tds:
                item = FundSpiderItem()
                item['fund_name'] = soup.find("option",selected='selected').text
                item['fund_full_name'] = soup.find("option",selected='selected').text
                item['foundation_date'] = itemTop['foundation_date']
                item['open_date'] =itemTop['open_date']
                item['nav'] = tds[1].text.strip()
                item['statistic_date'] = tds[0].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0066"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item
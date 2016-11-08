# -*- coding: utf-8 -*-
"""
万向信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import hashlib
from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "trust61_spider"
    allowed_domains = ["wxtrust.com"]

    start_urls = (
        'http://www.wxtrust.com/c55ef089-7d41-4e6c-8439-e5694694365e/index.html',
    )

    def parse(self, response):
        self.log(response.url)
        # 请求第一页
        yield scrapy.Request(response.url, callback=self.parse_two, dont_filter=True)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find('span', id="PageSpan").find_all("a")
        t = trs[1]['href']
        ts = filter(str.isdigit, t)
        for i in range(1, int(ts) + 1):
            url = "http://www.wxtrust.com/c55ef089-7d41-4e6c-8439-e5694694365e/index_%d.html" % i
            yield scrapy.Request(url, callback=self.parse_two)

    def parse_two(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find_all('dl')
        for tr in trs:
            years = tr.dd.text.replace("-", "")[0:4]
            urls = "http://www.wxtrust.com/c55ef089-7d41-4e6c-8439-e5694694365e/info/" + years + "/"
            idd = tr['id'].replace("vh_", "")
            urll = urls + idd + ".html"
            yield scrapy.Request(urll, callback=self.parse_history_nav)

    def parse_history_nav(self, response):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        trs = soup.find('div', {"class": "right_about"}).find_all("tr")
        for tr in trs:
            tds = tr.find_all('td')
            if tds:
                item = FundSpiderItem()
                item['fund_name'] = soup.find("div", {"class": "right_title"}).text.strip().replace("净值报告", "").replace(
                    "\r\n\t", "")
                item['fund_full_name'] = item['fund_name']
                item['nav'] = tds[1].text.strip()
                item['added_nav'] = tds[2].text.strip()
                item['statistic_date'] = tds[0].text.strip()
                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0061"
                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item
                yield item
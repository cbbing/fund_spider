# -*- coding: utf-8 -*-
"""
华融信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from bs4 import BeautifulSoup as bs
import re
import hashlib
import json
from selenium import webdriver
import time

import scrapy
from scrapy.http import FormRequest, HtmlResponse
from selenium import webdriver

from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime


class TrustHuaRongTrustSpider(scrapy.Spider):
    name = "trust14_huarongtrust_spider"
    allowed_domains = ["huarongtrust.com.cn"]

    start_urls = (
        'http://www.huarongtrust.com.cn/am/zjxtczjzpl.aspx',
    )

    # def start_requests(self):
    #     url = "http://www.fotic.com.cn/DesktopModules/ProductJZ/GetJsonResult.ashx"
    #     requests = []
    #     formdata = {"programName": "",
    #                 "sDate": "",
    #                 "eDate": "",
    #                 "pageNo": "1",
    #                 "pageSize": "10"
    #                 }
    #
    #     request = FormRequest(url, callback=self.parse, formdata=formdata)
    #     requests.append(request)
    #     return requests


    def parse(self, response):
        self.log(response.url)

        # 请求所有页
        soup = bs(response.body, 'lxml')
        pageSum = soup.find('a', text='尾页')
        if pageSum:
            findPage = re.search("\,\'(\d+)", pageSum['href'])
            if findPage:
                page_sum = int(findPage.group(1))
                driver = webdriver.PhantomJS()
                driver.get(response.url)
                driver.maximize_window()

                for i in range(page_sum):

                    time.sleep(3)
                    items = self.parse_body(driver.current_url, driver.page_source)
                    for item in items:
                        print item
                        yield item

                        # 历史净值
                        url = "http://www.huarongtrust.com.cn/am/s.aspx?i={}".format(item['fund_code'])
                        #yield scrapy.Request(url, callback=lambda response, item=item: self.parse_history_nav(response, item))

                    ele = driver.find_element_by_xpath("//a[contains(text(),'下一页')]")
                    ele.click()

                driver.quit()

                    # formdata = {
                    #     "__VIEWSTATEGENERATOR": "4A2FE269",
                    #     "__EVENTTARGET": "AspNetPager1",
                    #     "__EVENTARGUMENT": str(i),
                    #     "__EVENTVALIDATION": "/wEWBgK7nujMDgLs0bLrBgLs0fbZDALs0Yq1BQLs0e58AoznisYGho0giqf1dsYArTafHm5+ZTkaqtU=",
                    #     "TextBox1": "",
                    #     "TextBox2": "",
                    #     "TextBox3": "",
                    #     "TextBox4": "",
                    #     "__VIEWSTATE": "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"
                    # }
                    # yield FormRequest(response.url, callback=self.parse_item, formdata=formdata, dont_filter=True)

    def parse_body(self, current_url, content):
        self.log(current_url)

        items = []

        soup = bs(content, 'lxml')
        dds = soup.find_all('dd')
        for i in range(len(dds)):
            cs = ','.join(dds[i]['class'])
            if cs not in ('wid_01,hei_01', 'wid_01,bg_01') or i+8 >= len(dds):
                continue

            item = FundSpiderItem()

            item['fund_name'] = dds[i+1].text.strip()
            item['fund_full_name'] = item['fund_name']
            # item['open_date'] = tds[2].text.strip()
            item['nav'] = dds[i+3].text.strip()
            item['added_nav'] = dds[i+4].text.strip()
            item['foundation_date'] = dds[i+2].text.strip()
            item['statistic_date'] = dds[i+7].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = current_url
            item['org_id'] = 'TG0014'

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()

            # http: // www.ttco.cn / ttco / product_detail_founded?product.id = AF8A170DAC444375A47F368F28F83254
            href = dds[i+1].find('a')['href']
            findProId = re.search("i\s*=\s*(\w+)", href)
            if not findProId:
                continue
            item['fund_code'] = findProId.group(1)

            print item
            # yield item
            items.append(item)

            # 历史净值
            # url = "http://www.huarongtrust.com.cn/am/s.aspx?i={}".format(item['fund_code'])
            # yield scrapy.Request(url, callback=lambda response, item=item: self.parse_history_nav(response, item))

        return items

    # def parse_history_link(self, response, item):
    #     self.log(response.url)
    #
    #     # 获取当前页的历史净值
    #     yield scrapy.Request(response.url,
    #                          callback=lambda response, item=item: self.parse_history_nav(response, item),
    #                          dont_filter=True)
    #
    #     # 翻页
    #     urls = response.xpath('//a[contains(@href, "http://www.mintrust.com/wkxtweb//product/networthList?netWorths.start")]/@href').extract()
    #     for url in urls:
    #         # url = url if 'http' in url else "http://www.ttco.cn" + url
    #         yield scrapy.Request(url,
    #                              callback=lambda response, item=item: self.parse_history_nav(response, item))


    def parse_history_nav(self, response, itemTop):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) != 2 or tds[0].text.strip() == '估值日期':
                continue

            item = FundSpiderItem()
            item['fund_code'] = itemTop['fund_code']
            item['fund_name'] = itemTop['fund_name']
            item['fund_full_name'] = itemTop['fund_full_name']
            item['nav'] = tds[1].text.strip()
            # item['added_nav'] = tds[2].text.strip()
            item['foundation_date'] = itemTop['foundation_date']
            item['statistic_date'] = tds[0].text.strip()

            item['entry_time'] = GetNowTime()
            item['source_code'] = itemTop['source_code']
            item['source'] = response.url
            item['org_id'] = itemTop['org_id']

            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item






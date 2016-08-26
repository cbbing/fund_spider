# -*- coding: utf-8 -*-
"""
中江信托
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
from bs4 import BeautifulSoup as bs
import re
import hashlib
import os
import time
from scrapy.http import FormRequest

from fund_spider.items import FundSpiderItem
from util.codeConvert import GetNowTime
from fund_spider.helper.parsepdf import parse_pdf


class TrustJxiSpider(scrapy.Spider):
    name = "trust32_jxi_spider"
    allowed_domains = ["jxi.cn"]

    start_urls = (
        'http://www.jxi.cn/News.aspx?hl=Ch&id=32&PageIndex=1',
    )

    # def start_requests(self):
    #     url = "http://www.huabaotrust.com/index111.jsp"
    #     requests = []
    #     for i in range(1, 7):
    #         formdata = {"show": "0",
    #                     "pageIndex": str(i),
    #                     "totalSize": "30",
    #                    }
    #         request = FormRequest(url, callback=self.parse, formdata=formdata)
    #         requests.append(request)
    #     return requests


    def parse(self, response):
        self.log(response.url)

        # 请求第一页
        yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)

        # 请求其它页
        hrefs = response.xpath("//div/a[contains(@href, '/News.aspx?hl=Ch&id=32&PageIndex=')]/@href").extract()
        page_list = []
        for href in hrefs:
            findPage = re.search("PageIndex=(\d+)", href)
            if findPage:
                page_list.append(int(findPage.group(1)))

        total_page = max(page_list)
        for i in range(2, total_page + 1):
            href = "http://www.jxi.cn/News.aspx?hl=Ch&id=32&PageIndex={}".format(i)
            yield scrapy.Request(href, callback=self.parse_item)


    def parse_item(self, response):
        self.log(response.url)

        soup = bs(response.body, 'lxml')
        a_tags = soup.find_all('a', {'href':re.compile('/NewsView.aspx\?id=\w+&hl=Ch')})
        for a in a_tags:
            if '净值' in a.text:
                href = a['href']
                href = href if 'http' in href else "http://www.jxi.cn" + href
                yield scrapy.Request(href, callback=self.parse_history_link)


    # def parse_item_plus(self, response, item):
    #     self.log(response.url)
    #
    #     soup = bs(response.body, 'lxml')
    #     trs = soup.find_all('tr')
    #     if len(trs) == 6:
    #         tds = trs[2].find_all('td')
    #         if len(tds) and tds[0].text.strip() == "产品建立日期":
    #             item['foundation_date'] = tds[1].text.strip()
    #
    #     print item
    #     yield item
    #
    #     # 产品历史净值
    #     href_history = "http://www.huabaotrust.com/mouyichanpinlishi.jsp?product_id={fund_code}&prod_period_no=0001". \
    #         format(fund_code=item['fund_code'])
    #     yield scrapy.Request(href_history, callback=lambda response, itemTop=item: self.parse_history_link(response, itemTop))

    def parse_history_link(self, response):
        """
        历史净值链接
        :param response:
        :return:
        """

        self.log(response.url)

        soup = bs(response.body, 'lxml')
        pdfLink = soup.find('a', {'href':re.compile('.*\.pdf')})
        if pdfLink:
            href = pdfLink['href']
            href = href if 'http' in href else "http://www.jxi.cn" + href
            yield scrapy.Request(href, callback=self.parse_history_nav)


    def parse_history_nav(self, response):
        """
        历史净值pdf
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)

        dir = 'fund_spider/tmp'
        if not os.path.exists(dir):
            os.makedirs(dir)

        suffixFind = re.search('/(\w+)/(\w+.pdf)', response.url)
        if suffixFind:
            filename = dir + '/' + suffixFind.group(1) + '-' + suffixFind.group(2)
        else:
            filename = hashlib.md5(response.url).hexdigest()

        f = open(filename , 'wb')
        f.write(response.body)
        f.close()

        contents = parse_pdf(filename)
        content = '\n'.join(contents)
        contents = content.split('\n')

        names = []
        foundation_dates = []
        navs = []
        statistic_date = None
        for c in contents:

            if '披露日' in c:
                findDate = re.search(u"披露日：\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})", c)
                if findDate:
                    statistic_date = "{}-{}-{}".format(findDate.group(1), findDate.group(2), findDate.group(3))
            elif '信托业务' in c or '产品名称' in c or '成立' in c:
                continue
            elif '净值' in c or '估值' in c:
                continue
            elif '年' in c:
                foundation_dates.append(c)
            elif c.replace('.', '').isdigit():
                navs.append(c)
            else:
                names.append(c)

        if len(names) == len(navs) and statistic_date:
            for ix in range(len(names)):
                item = FundSpiderItem()
                item['fund_name'] = re.sub('\s','', names[ix])
                item['fund_full_name'] = item['fund_name']
                item['nav'] = navs[ix].strip()
                item['statistic_date'] = statistic_date

                if len(foundation_dates) == len(navs):
                    item['foundation_date'] = re.sub('\s','', foundation_dates[ix])
                    item['foundation_date'] = item['foundation_date'].replace('年', '-').replace('月','-').replace('日','')

                item['entry_time'] = GetNowTime()
                item['source_code'] = 1
                item['source'] = response.url
                item['org_id'] = "TG0032"

                item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
                print item['fund_name']
                print item
                yield item


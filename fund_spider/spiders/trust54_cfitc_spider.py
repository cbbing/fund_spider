# -*- coding: utf-8 -*-
"""
华鑫信托
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from bs4 import BeautifulSoup
import re
import hashlib
from fund_spider.items import FundSpiderItem
from util.date_convert import GetNowTime
class TrustSxxtSpider(scrapy.Spider):
    name = "trust54_spider"
    allowed_domains = ["cfitc.com"]

    start_urls = (

    'http://www.cfitc.com/webfront/webpage/web/contentList/channelId/c8f5402dc3de432ab57257d2d652787b/pageNo/1',

    )


    def parse(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        s = soup.find_all("script", type="text/javascript")
        for i in s:
            if 'pageNum' in i.text:
                total_page = re.search("pageNum\s*=(.*?)\s*\;", i.text).group(1)
                for page in range(1, int(total_page) + 1):
                    url = "http://www.cfitc.com/nodejsService/articleListSearch/?website_id=c8f5402dc3de432ab57257d2d652787b&perPage=20&startNum=%d&_=1473040141681" % page
                    yield scrapy.Request(url, callback=self.get_two)




    def get_two(self,response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")
        t = soup.text.replace("callbackMethod([", "").replace("])", "")
        tt = t.replace(",", ',"').replace(":", '":').replace("{", '[{"').replace("}", "}]").replace('],"[', ",")
        kk = tt.replace("[", "").replace("]", "")
        target_list = [x for x in kk.split('}')]
        for i in target_list:
            s = re.compile('"ID"\:\'(.*?)\'\,')
            if s:
                try:
                    item = FundSpiderItem()
                    titles = re.search(re.compile('"TITLE"\:\'(.*?)\'\,'), i).group(1)
                    item['fund_full_name']=titles
                    tt = re.search(s, i).group(1)
                    urll="http://www.cfitc.com/webfront/webpage/web/contentPage/id/"+tt
                    yield scrapy.Request(urll,callback=lambda response, item=item: self.parse_history_nav(response, item))
                except:
                    pass



    def parse_history_nav(self, response,firstitem):
        """
        历史净值
        :param response:
        :param itemTop:
        :return:
        """
        self.log(response.url)
        soup = BeautifulSoup(response.body, "lxml")

        trs = soup.find_all('tr')
        for tr in trs:
            ps = tr.find_all('td')
            if len(ps[0].text.strip()) < 5:
                continue

            # if "日期" == ps[0].text:
            #     continue
            item = FundSpiderItem()
            item['fund_name'] = item['fund_name'].replace("净值公告","")
            item['fund_full_name'] = item['fund_name']
            item['statistic_date'] = ps[0].text.strip()
            item['nav'] = ps[1].text.strip()
            item['entry_time'] = GetNowTime()
            item['source_code'] = 1
            item['source'] = response.url
            item['org_id'] = "TG0054"
            item['uuid'] = hashlib.md5((item['fund_name'] + item['statistic_date']).encode('utf8')).hexdigest()
            print item
            yield item
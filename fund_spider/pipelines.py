# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis
import pandas as pd
from sqlalchemy import create_engine

from scrapy.exceptions import DropItem
from items import FundSpiderItem
import fund_spider.settings as settings

engine = create_engine('mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER, settings.MYSQL_PASSWD, settings.MYSQL_HOST, settings.MYSQL_DBNAME) , connect_args={'charset': 'utf8'})
redis_db4 = redis.Redis(host=settings.REDIS_HOST, port=6379, db=4, password=settings.REDIS_PWD)
redis_fund_dict = "fund_ids"

class DuplicatePipeline(object):
    """
    去重(redis)
    """

    def __init__(self):
        #df = pd.read_sql('select uuid from article_guba_easymoney', engine)
        #self.uuids_seen = set(df['uuid'].get_values())
        # self.uuids_seen = []
        pass


    def process_item(self, item, spider):

        if type(item) is FundSpiderItem:

            if redis_db4.hexists(redis_fund_dict, item['uuid']):
                raise DropItem("Duplicate item found:%s" % item)



        return item

class MySQLStorePipeline(object):

    def __init__(self):
        self.fund_items = {}

    def process_item(self, item, spider):

        # self.fund_items.setdefault(spider.name, [])
        # self.fund_items[spider.name].append(item)
        df = pd.DataFrame([item])
        print df
        df.to_sql('fund_nav', engine, if_exists='append', index=False)
        redis_db4.hset(redis_fund_dict, item['uuid'], 0)

        return item

    def close_spider(self, spider):
        pass

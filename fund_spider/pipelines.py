# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import redis
import pandas as pd
from sqlalchemy import create_engine
import threading

from scrapy.exceptions import DropItem
from items import FundSpiderItem
import fund_spider.settings as settings

engine = create_engine('mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER, settings.MYSQL_PASSWD, settings.MYSQL_HOST, settings.MYSQL_DBNAME) ,
                       connect_args={'charset': 'utf8'},
                       pool_size=8)
redis_db4 = redis.Redis(host=settings.REDIS_HOST, port=6379, db=4, password=settings.REDIS_PWD)
redis_fund_dict = "fund_uuids"

mysql_table = "t_fund_nv_data"

mutex = threading.Lock()

class DuplicatePipeline(object):
    """
    去重(redis)
    """

    def __init__(self):
        if redis_db4.hlen(redis_fund_dict) == 0:
            sql = "SELECT uuid FROM {}".format(mysql_table)
            df = pd.read_sql(sql, engine)
            for uuid in df['uuid'].get_values():
                redis_db4.hset(redis_fund_dict, uuid, 0)

    def process_item(self, item, spider):

        if type(item) is FundSpiderItem:
            if redis_db4.hexists(redis_fund_dict, item['uuid']):
                raise DropItem("Duplicate item found:%s" % item)

        return item

class SetFundIDPipeline(object):
    """
    设置fund_id字段
    """
    def process_item(self, item, spider):

        if mutex.acquire(): # 互斥锁 加锁

            sql = "select distinct fund_id from {} where fund_name='{}' ".format(mysql_table, item['fund_name'])
            df = pd.read_sql(sql, engine)
            fund_ids = df['fund_id'].get_values()
            if len(fund_ids) and fund_ids[0]: # 数据库中存在fund_id, 直接赋值
                item['fund_id'] = fund_ids[0]
            else:  # 数据库中不存在, 新建一个fund_id
                sql = "SELECT distinct fund_id FROM {}  where org_id ='{}' order by length(fund_id) desc, fund_id desc".format(
                    mysql_table, item['org_id']
                )
                df = pd.read_sql(sql, engine)
                fund_ids = df['fund_id'].get_values()
                if len(fund_ids) and fund_ids[0]:
                    find_last_id = re.search("XT(\d+)", fund_ids[0])
                    if find_last_id:
                        last_id = int(find_last_id.group(1))+1
                    index = '0'+str(last_id) if last_id < 10 else str(last_id)
                    new_fund_id = item['org_id'] + "XT" + index
                else:
                    new_fund_id = item['org_id'] + "XT" + "01"

                item['fund_id'] = new_fund_id

            mutex.release()  # 互斥锁 释放
        return item







class MySQLStorePipeline(object):

    def __init__(self):
        self.fund_items = {}

    def process_item(self, item, spider):

        # self.fund_items.setdefault(spider.name, [])
        # self.fund_items[spider.name].append(item)
        df = pd.DataFrame([item])
        print df
        df.to_sql(mysql_table, engine, if_exists='append', index=False)
        redis_db4.hset(redis_fund_dict, item['uuid'], item['org_id'])

        return item

    def close_spider(self, spider):
        pass

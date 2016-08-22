#coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import pandas as pd
from sqlalchemy import create_engine
import fund_spider.settings as settings

engine_src = create_engine(
    'mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER, settings.MYSQL_PASSWD, settings.MYSQL_HOST,
                                              settings.MYSQL_DBNAME), connect_args={'charset': 'utf8'})

engine_obj = create_engine(
    'mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER_OBJ, settings.MYSQL_PASSWD_OBJ, settings.MYSQL_HOST_OBJ,
                                              settings.MYSQL_DBNAME_OBJ),connect_args={'charset': 'utf8'})

def synchronize_to_db():
    sql = "select uuid, org_id, fund_id, fund_name, fund_full_name, open_date, nav, added_nav, foundation_date, statistic_date, entry_time, " \
          "source_code, source from classifier_db.t_fund_nv_data where syn_status=0"
    datas = pd.read_sql(sql, engine_src, chunksize=1000)
    for df in datas:
        uuids = df['uuid'].get_values()

        del df['uuid']

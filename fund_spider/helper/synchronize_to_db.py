#coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import time
import pandas as pd
from sqlalchemy import create_engine
import redis
import fund_spider.settings as settings

engine_src = create_engine(
    'mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER, settings.MYSQL_PASSWD, settings.MYSQL_HOST,
                                              settings.MYSQL_DBNAME), connect_args={'charset': 'utf8'})

engine_obj = create_engine(
    'mysql+mysqldb://{}:{}@{}:3306/{}'.format(settings.MYSQL_USER_OBJ, settings.MYSQL_PASSWD_OBJ, settings.MYSQL_HOST_OBJ,
                                              settings.MYSQL_DBNAME_OBJ),connect_args={'charset': 'utf8'})

redis_db4 = redis.Redis(host=settings.REDIS_HOST, port=6379, db=4, password=settings.REDIS_PWD)
redis_key_syn_dict = "fund_syn_to_fof_uuids"

def synchronize_to_db():

    for i in range(1, 70):
        org_id = 'TG000{}'.format(i) if i < 10 else 'TG00{}'.format(i)

        # 源数据
        sql = "select uuid, org_id, fund_id, fund_name, fund_full_name, open_date, nav, added_nav, foundation_date, statistic_date, entry_time, " \
              "source_code, source from classifier_db.t_fund_nv_data where org_id='{}' and syn_status=0 ".format(org_id) #and syn_status=0
        datas = pd.read_sql(sql, engine_src, chunksize=1000)


        for df_origin in datas:
            if len(df_origin) == 0:
                continue

            print org_id, 'save to db begin...'
            for ix, row in df_origin.iterrows():
                try:
                    df_origin[ix:ix+1].to_sql("t_fund_nv_data", engine_obj, if_exists='append', index=False)
                    print row['uuid']
                except Exception,e:
                    print "{} exists".format(row['uuid'])

                sql_u = "update classifier_db.t_fund_nv_data set syn_status=1 where uuid='{}' ".format(row['uuid'])
                engine_src.execute(sql_u)

            print org_id, 'save to db end...'

            # uuids = df_origin['uuid'].get_values()
            #
            # print org_id, 'before len', len(df_origin)
            # df = df_origin[df_origin['uuid'].apply(lambda x: not redis_db4.hexists(redis_key_syn_dict, x))]
            # print org_id,  'after len', len(df)
            # # del df['uuid']
            # print df.head(1)
            # # print df.columns
            #
            # print org_id, 'save to db begin...'
            # df.to_sql("t_fund_nv_data", engine_obj, if_exists='append', index=False)
            # print org_id, 'save to db finish...'
            #
            # print org_id,  'update status to redis begin...'
            # for uuid in uuids:
            #     redis_db4.hset(redis_key_syn_dict, uuid, 0)
            # print org_id, 'update status to redis finish...'
            #
            # print org_id,  'update status begin...'
            # for uuid in uuids:
            #     sql_u = "update classifier_db.t_fund_nv_data set syn_status=1 where uuid='{}' ".format(uuid)
            #     engine_src.execute(sql_u)
            # print org_id, 'update status finished'

        print 'syn {} finished! sleep 3 seconds'.format(org_id)
        time.sleep(3)

if __name__ == "__main__":
    synchronize_to_db()
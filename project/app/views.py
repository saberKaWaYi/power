import os
import logging
from logging.handlers import RotatingFileHandler

log_dir="logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir,"app.log"),
            maxBytes=1024*1024*1024,
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

import atexit
from clickhouse_driver import Client
import time
import pandas as pd

class Connect_Clickhouse:

    def __init__(self,config):
        self.config=config
        self.client=self.login()
        atexit.register(self.close)

    def login(self):
        for i in range(self.config["connection"]["TIMES"]):
            try:
                client=Client(host=self.config["clickhouse"]["HOST"],port=self.config["clickhouse"]["PORT"],user=self.config["clickhouse"]["USERNAME"],password=self.config["clickhouse"]["PASSWORD"])
                return client
            except:
                time.sleep(self.config["connection"]["TIME"])
        logging.error("clickhouse登录失败。")
        raise Exception("clickhouse登录失败。")
    
    def close(self):
        for i in range(self.config["connection"]["TIMES"]):
            try:
                self.client.disconnect()
                return
            except:
                time.sleep(self.config["connection"]["TIME"])
        logging.error("clickhouse关闭失败。")
        raise Exception("clickhouse关闭失败。")
    
    def query(self,query):
        for i in range(self.config["connection"]["TIMES"]):
            try:
                data,columns=self.client.execute(query,with_column_types=True)
                columns=[col[0] for col in columns]
                data=pd.DataFrame(data,columns=columns).astype(str)
                return data
            except:
                time.sleep(self.config["connection"]["TIME"])
        logging.error(f"{query}数据获取失败。")
        raise Exception(f"{query}数据获取失败。")

config={
    "connection":{
        "TIMES":1000,
        "TIME":0.1
    },
    "clickhouse":{
        "HOST":"10.216.140.107",
        "PORT":9000,
        "USERNAME":"default",
        "PASSWORD":""
    }
}
# config={
#     "connection":{
#         "TIMES":1000,
#         "TIME":0.1
#     },
#     "clickhouse":{
#         "HOST":"localhost",
#         "PORT":5001,
#         "USERNAME":"default",
#         "PASSWORD":""
#     }
# }

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def get_data(request):
    return Response(request.data)

from datetime import datetime,timedelta

@api_view(['GET'])
def menu_data(request):
    zd={}
    zd["code"]=200;zd["msg"]=""
    conn=Connect_Clickhouse(config)
    client=conn.client
    end_time=datetime.now()
    start_time=end_time-timedelta(days=1)
    start_str=start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_str=end_time.strftime('%Y-%m-%d %H:%M:%S')
    query=f'''
    SELECT city,data_center,room,rack FROM power.power_data WHERE ts >='{start_str}' AND ts<='{end_str}'
    '''
    data=conn.query(query).values.tolist()
    logging.info(data)
    logging.info(config)
    temp={}
    for i in data:
        a,b,c,d=i[0],i[1],i[2],i[3]
        s=a+"-"+b+"-"+c
        if s not in temp:
            temp[s]=set()
        temp[s].add(d)
    zd["data"]=[]
    for i in temp:
        zd_temp={}
        zd_temp["code"]=i
        zd_temp["name"]=i
        zd_temp["rack_list"]=sorted(list(temp[i]))
        zd["data"].append(zd_temp)
    return Response(zd)
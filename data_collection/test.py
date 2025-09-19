# from connect import Connect_Clickhouse

# if __name__=="__main__":
#     config={
#         "connection":{
#             "TIMES":1000,
#             "TIME":0.1
#         },
#         "clickhouse":{
#             "HOST":"10.216.140.107",
#             "PORT":9000,
#             "USERNAME":"default",
#             "PASSWORD":""
#         }
#     }
#     conn=Connect_Clickhouse(config)
#     data=conn.query("SELECT * FROM power.power_data limit 1")
#     print(data)
# from get_relationship import get_relationship,get_ObjectId

# if __name__=="__main__":
#     config={
#         "connection":{
#             "TIMES":1000,
#             "TIME":0.1
#         },
#         "mongodb":{
#             "HOST":"10.216.141.46",
#             "PORT":27017,
#             "USERNAME":"manager",
#             "PASSWORD":"cds-cloud@2017"
#         }
#     }
#     zd=get_relationship(config,get_ObjectId(config,"庆阳"))
#     count=0
#     for i in zd:
#         for j in zd[i]:
#             if j[-1]=="network":
#                 count+=1
#     print(count)
# import requests

# if __name__=="__main__":
#     hostname="USDAL-DB2-J10003-C-01"
#     url_post='http://10.213.136.111:40061/network_app/distribute_config/exec_cmd/'
#     config={
#         "device_hostname":hostname,
#         "operator":"LCL",
#         "is_edit":False,
#         "cmd":""
#     }
#     url_get=f"http://10.216.142.10:40061/network_app/conf/device/data_list/?device_hostname={hostname}"
#     response_url_get=requests.get(url_get).json()
#     try:
#         client_names=response_url_get["data"][0]["net_data"]
#     except Exception as e:
#         print("="*50+"\njson解析错误\n"+str(e)+"\n"+"="*50)
#     if client_names:
#         temp=[]
#         for client_name in client_names:
#             if client_name["operator"]!="LCL":
#                 continue
#             temp.append((client_names[client_name]["client_name"],client_names[client_name]["created_at"]))
#         temp.sort(key=lambda x:x[1])
#         config["client_name"]=temp[-1][0]
#     config["cmd"]="show chassis environment pem"
#     response=requests.post(url_post,json=config)
#     data=response.json()["data"]["cmd_result"]
#     if not data and "client_name" in config:
#         del config["client_name"]
#         response=requests.post(url_post,json=config)
#         data=response.json()["data"]["cmd_result"]
#     print("测试成功")
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
import requests

if __name__=="__main__":
    url_post='http://10.213.136.111:40061/network_app/distribute_config/exec_cmd/'
    config={
        "device_hostname":"CNIQN-POD235-F69-CL-17",
        "operator":"devops",
        "is_edit":False,
        "cmd":""
    }
    config["cmd"]="show power"
    response=requests.post(url_post,json=config)
    data=response.json()["data"]["cmd_result"]
    if not data and "client_name" in config:
        del config["client_name"]
        response=requests.post(url_post,json=config)
        data=response.json()["data"]["cmd_result"]
    print(data)
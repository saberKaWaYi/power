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
# from redfish import AMI

# if __name__=="__main__":
#     m=AMI("10.194.26.12","ADMIN","ADMIN@123")
#     print(m.get_psu_detail())
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import base64
import requests
import time

def fc1(idrac_ip,username,password):
    try:
        def b64(s):
            return base64.b64encode(s.encode("utf-8")).decode("ascii")
        BMC_HOST="https://"+idrac_ip
        sess=requests.Session()
        sess.verify=False
        sess.cookies.set("lang","zh-cn",domain=idrac_ip,path="/")
        login_url=f"{BMC_HOST}/api/session"
        login_headers={
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "Accept":"application/json, text/javascript, */*; q=0.01",
            "X-CSRFTOKEN":"null",
            "X-Requested-With":"XMLHttpRequest",
            "Origin":BMC_HOST,
            "Referer":BMC_HOST+"/",
        }
        login_data={
            "username":b64(username),
            "password":b64(password),
        }
        resp=sess.post(login_url,headers=login_headers,data=login_data,timeout=15)
        info=resp.json()
        csrf=info.get("CSRFToken",None)
        if not csrf:
            return [[0.00,0.00,0.00]]
        api_headers={
            "Accept":"application/json",
            "X-CSRFTOKEN":csrf,
            "X-Requested-With":"XMLHttpRequest",
            "Referer":BMC_HOST+"/",
        }
        detail_url=f"{BMC_HOST}/api/detail_sensors_readings"
        p=[];v=[]
        for _ in range(18):
            data=sess.get(detail_url,headers=api_headers,timeout=15).json()
            for j in data:
                if j["name"]=="SYS_Total_Power":
                    p.append(j["reading"])
                if "PSU" in j["name"] and "Vin" in j["name"]:
                    v.append(j["reading"])
            time.sleep(5)
        p=max(p);v=sum(v)/len(v)
        return [[round(v,2),round(p/v,2),round(p,2)]]
    except:
        return [[0.00,0.00,0.00]]
    
import subprocess

def fc2(idrac_ip,username,password):
    command="ipmitool -I lanplus -H "+idrac_ip+" -U "+username+" -P "+f"\'{password}\' "+"sensor | grep PSU"
    process=subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    a=[];b=[];c=[]
    for line in process.stdout.strip().split("\n"):
        try:
            x=eval(line.split("|")[1])
            if "vin" in line.lower():
                a.append(x)
            if "iin" in line.lower():
                b.append(x)
            if "pin" in line.lower():
                c.append(x)
        except:
            pass
    a=sum(a)/len(a) if a else 0
    c=sum(c)
    b=sum(b) if b else c/a if a else 0
    return [[round(a,2),round(b,2),round(c,2)]]

if __name__=="__main__":
    print(fc2("10.213.35.86","ADMIN","ADMIN@123"))
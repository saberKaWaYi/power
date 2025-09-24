# import subprocess

# def fc(idrac_ip,username,password):
#     command="ipmitool -I lanplus -H "+idrac_ip+" -U "+username+" -P "+f"\'{password}\' "+"sensor | grep PSU"
#     process=subprocess.run(
#         command,
#         shell=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         universal_newlines=True
#     )
#     a=[];b=0;c=0
#     for line in process.stdout.strip().split("\n"):
#         if "vin" in line.lower():
#             a.append(eval(line.split("|")[1]))
#         if "pin" in line.lower():
#             c+=eval(line.split("|")[1])
#     a=sum(a)/len(a);b=c/a
#     return [[round(a,2),round(b,2),round(c,2)]]

# if __name__=="__main__":
#     print(fc("10.194.26.3","ADMIN","ADMIN@123"))
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import base64
import requests

import time

def fc(idrac_ip,username,password):
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
        for _ in range(24):
            data=sess.get(detail_url,headers=api_headers,timeout=15).json()
            for j in data:
                if j["name"]=="SYS_Total_Power":
                    p.append(j["reading"])
                if "PSU" in j["name"] and "Vin" in j["name"]:
                    v.append(j["reading"])
            time.sleep(5)
        p.sort(reverse=True)
        p=p[len(p)//4];v=sum(v)/len(v)
        return [[round(v,2),round(p/v,2),round(p,2)]]
    except:
        return [[0.00,0.00,0.00]]

if __name__=="__main__":
    print(fc("10.194.26.3","ADMIN","ADMIN@123"))
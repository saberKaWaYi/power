import os
import logging
from logging.handlers import RotatingFileHandler
import base64
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

class Dell:

    def __init__(self,idrac_ip,username="root",password="P@$$w0rd"):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.headers={
            'Authorization':f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}',
            'Content-Type':'application/json'
        }

    def get_psu_detail(self):
        url=f"{self.base_url}/Chassis/System.Embedded.1/Power"
        response=requests.get(
            url,
            verify=False,
            headers=self.headers,
            timeout=60
        )
        try:
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]
        
class Inspur:

    def __init__(self,idrac_ip,username="admin",password="P@$$w0rd"):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session()
        self.session.verify=False
        self._login()

    def _login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        response=self.session.post(
            login_url,
            json=data,
            verify=False,
            timeout=60
        )
        self.session.headers.update({
            'X-Auth-Token':response.headers.get('X-Auth-Token'),
            'Content-Type':'application/json'
        })

    def get_psu_detail(self):
        url=f"{self.base_url}/Chassis/1/Power"
        response=self.session.get(url,timeout=60)
        try:
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                result.append([i["LineInputVoltage"],eval(i["Oem"]["InputCurrent"]),i["LineInputVoltage"]*eval(i["Oem"]["InputCurrent"])])
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]
        
class Xfusion:

    def __init__(self,idrac_ip,username="ADMIN",password="ADMIN@123"):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session()
        self.session.verify=False
        self._login()

    def _login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        response=self.session.post(
            login_url,
            json=data,
            verify=False,
            timeout=60
        )
        self.session.headers.update({
            'X-Auth-Token':response.headers.get('X-Auth-Token'),
            'Content-Type':'application/json'
        })

    def get_psu_detail(self):
        url=f"{self.base_url}/Chassis/1/Power"
        response=self.session.get(url,timeout=60)
        try:
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]

class AMI:

    def __init__(self,idrac_ip,username="ADMIN",password="ADMIN@123"):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session()
        self.session.verify=False
        self._login()

    def _login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        response=self.session.post(
            login_url,
            json=data,
            verify=False,
            timeout=60
        )
        self.session.headers.update({
            'X-Auth-Token':response.headers.get('X-Auth-Token'),
            'Content-Type':'application/json'
        })

    def get_psu_detail(self):
        url=f"{self.base_url}/Chassis/Self/Power"
        response=self.session.get(url,timeout=60)
        try:
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]

if __name__=="__main__":
    idrac_ip="10.212.121.37"
    m=AMI(idrac_ip)
    print(m.get_psu_detail())
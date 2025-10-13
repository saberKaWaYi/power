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

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import atexit

class Supermicro:

    def __init__(self,idrac_ip,username,password):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session();self.session.verify=False
        self.session_id=None
        self.error_reason=None
        atexit.register(self.logout)
        self.login()

    def login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        try:
            response=self.session.post(
                login_url,
                json=data,
                verify=False,
                timeout=60
            )
            if response.status_code==201:
                self.session_id=response.headers['Location'].split('/')[-1]
                self.session.headers.update({
                    'X-Auth-Token':response.headers.get('X-Auth-Token'),
                    'Content-Type':'application/json'
                })
            elif response.status_code==401:
                self.error_reason="="*50+f"\n{self.idrac_ip}密码不对\n"+"="*50
                logging.error(self.error_reason)
            else:
                self.error_reason="="*50+f"\n{self.idrac_ip}未知状态码\n"+"="*50
                logging.error(self.error_reason)
        except Exception as e:
            self.error_reason="="*50+f"\n{self.idrac_ip}网络不通\n"+str(e)
            logging.error(self.error_reason)

    def test(self):
        print(self.session_id)

    def logout(self):
        if not self.session_id:
            return
        try:
            logout_url=f"{self.base_url}/SessionService/Sessions/{self.session_id}"
            self.session.delete(logout_url,timeout=60)
            self.session.close()
            self.session_id=None
        except:
            logging.error(f"{self.idrac_ip}退出失败")

    def get_psu_detail(self):
        if not self.session_id:
            return [[0.00,0.00,0.00,0.00]]
        url=f"{self.base_url}/Chassis/1/Power"
        try:
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                try:
                    result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
                except:
                    pass
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]

class Dell:

    def __init__(self,idrac_ip,username,password):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session();self.session.verify=False
        self.session_id=None
        self.error_reason=None
        atexit.register(self.logout)
        self.login()

    def login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        try:
            response=self.session.post(
                login_url,
                json=data,
                verify=False,
                timeout=60
            )
            if response.status_code==201:
                self.session_id=response.headers['Location'].split('/')[-1]
                self.session.headers.update({
                    'X-Auth-Token':response.headers.get('X-Auth-Token'),
                    'Content-Type':'application/json'
                })
            elif response.status_code==401:
                self.error_reason="="*50+f"\n{self.idrac_ip}密码不对\n"+"="*50
                logging.error(self.error_reason)
            else:
                self.error_reason="="*50+f"\n{self.idrac_ip}未知状态码\n"+"="*50
                logging.error(self.error_reason)
        except Exception as e:
            self.error_reason="="*50+f"\n{self.idrac_ip}网络不通\n"+str(e)
            logging.error(self.error_reason)

    def test(self):
        print(self.session_id)

    def logout(self):
        if not self.session_id:
            return
        try:
            logout_url=f"{self.base_url}/SessionService/Sessions/{self.session_id}"
            self.session.delete(logout_url,timeout=60)
            self.session.close()
            self.session_id=None
        except:
            logging.error(f"{self.idrac_ip}退出失败")

    def get_psu_detail(self):
        if not self.session_id:
            return [[0.00,0.00,0.00,0.00]]
        url=f"{self.base_url}/Chassis/System.Embedded.1/Power"
        try:
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]
        
class Inspur:

    def __init__(self,idrac_ip,username,password):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session();self.session.verify=False
        self.session_id=None
        self.error_reason=None
        atexit.register(self.logout)
        self.login()

    def login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        try:
            response=self.session.post(
                login_url,
                json=data,
                verify=False,
                timeout=60
            )
            if response.status_code==201:
                self.session_id=response.headers['Location'].split('/')[-1]
                self.session.headers.update({
                    'X-Auth-Token':response.headers.get('X-Auth-Token'),
                    'Content-Type':'application/json'
                })
            elif response.status_code==401:
                self.error_reason="="*50+f"\n{self.idrac_ip}密码不对\n"+"="*50
                logging.error(self.error_reason)
            else:
                self.error_reason="="*50+f"\n{self.idrac_ip}未知状态码\n"+"="*50
                logging.error(self.error_reason)
        except Exception as e:
            self.error_reason="="*50+f"\n{self.idrac_ip}网络不通\n"+str(e)
            logging.error(self.error_reason)

    def test(self):
        print(self.session_id)

    def logout(self):
        if not self.session_id:
            return
        try:
            logout_url=f"{self.base_url}/SessionService/Sessions/{self.session_id}"
            self.session.delete(logout_url,timeout=60)
            self.session.close()
            self.session_id=None
        except:
            logging.error(f"{self.idrac_ip}退出失败")

    def get_psu_detail(self):
        if not self.session_id:
            return [[0.00,0.00,0.00,0.00]]
        url=f"{self.base_url}/Chassis"
        try:
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            url=f"https://{self.idrac_ip}"+response.json()["Members"][0]
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            url=f"https://{self.idrac_ip}"+response.json()["Power"]['@odata.id']
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                result.append([i["LineInputVoltage"],eval(i["Oem"]["InputCurrent"]),i["LineInputVoltage"]*eval(i["Oem"]["InputCurrent"])])
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]
        
class Xfusion:

    def __init__(self,idrac_ip,username,password):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session();self.session.verify=False
        self.session_id=None
        self.error_reason=None
        atexit.register(self.logout)
        self.login()

    def login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        try:
            response=self.session.post(
                login_url,
                json=data,
                verify=False,
                timeout=60
            )
            if response.status_code==201:
                self.session_id=response.headers['Location'].split('/')[-1]
                self.session.headers.update({
                    'X-Auth-Token':response.headers.get('X-Auth-Token'),
                    'Content-Type':'application/json'
                })
            elif response.status_code==401:
                self.error_reason="="*50+f"\n{self.idrac_ip}密码不对\n"+"="*50
                logging.error(self.error_reason)
            else:
                self.error_reason="="*50+f"\n{self.idrac_ip}未知状态码\n"+"="*50
                logging.error(self.error_reason)
        except Exception as e:
            self.error_reason="="*50+f"\n{self.idrac_ip}网络不通\n"+str(e)
            logging.error(self.error_reason)

    def test(self):
        print(self.session_id)

    def logout(self):
        if not self.session_id:
            return
        try:
            logout_url=f"{self.base_url}/SessionService/Sessions/{self.session_id}"
            self.session.delete(logout_url,timeout=60)
            self.session.close()
            self.session_id=None
        except:
            logging.error(f"{self.idrac_ip}退出失败")

    def get_psu_detail(self):
        if not self.session_id:
            return [[0.00,0.00,0.00,0.00]]
        url=f"{self.base_url}/Chassis/1/Power"
        try:
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            lt=response.json()["PowerSupplies"]
            result=[]
            for i in lt:
                try:
                    result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
                except:
                    pass
            return result
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]

from tool import fc1

class AMI:

    def __init__(self,idrac_ip,username,password):
        self.idrac_ip=idrac_ip
        self.username=username
        self.password=password
        self.base_url=f"https://{self.idrac_ip}/redfish/v1"
        self.session=requests.Session();self.session.verify=False
        self.session_id=None
        self.error_reason=None
        atexit.register(self.logout)
        self.login()

    def login(self):
        login_url=f"{self.base_url}/SessionService/Sessions"
        data={
            "UserName":self.username,
            "Password":self.password
        }
        try:
            response=self.session.post(
                login_url,
                json=data,
                verify=False,
                timeout=60
            )
            if response.status_code==201:
                self.session_id=response.headers['Location'].split('/')[-1]
                self.session.headers.update({
                    'X-Auth-Token':response.headers.get('X-Auth-Token'),
                    'Content-Type':'application/json'
                })
            elif response.status_code==401:
                self.error_reason="="*50+f"\n{self.idrac_ip}密码不对\n"+"="*50
                logging.error(self.error_reason)
            else:
                self.error_reason="="*50+f"\n{self.idrac_ip}未知状态码\n"+"="*50
                logging.error(self.error_reason)
        except Exception as e:
            self.error_reason="="*50+f"\n{self.idrac_ip}网络不通\n"+str(e)
            logging.error(self.error_reason)

    def test(self):
        print(self.session_id)

    def logout(self):
        if not self.session_id:
            return
        try:
            logout_url=f"{self.base_url}/SessionService/Sessions/{self.session_id}"
            self.session.delete(logout_url,timeout=60)
            self.session.close()
            self.session_id=None
        except:
            logging.error(f"{self.idrac_ip}退出失败")

    def get_psu_detail(self):
        if not self.session_id:
            return [[0.00,0.00,0.00,0.00]]
        try:
            url=f"{self.base_url}/Chassis/1/Power"
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            if response.status_code==200:
                lt=response.json()["PowerSupplies"]
                if "PowerInputWatts" not in lt[0]:
                    return fc(self.idrac_ip,self.username,self.password)
                result=[]
                for i in lt:
                    result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
                return result
            url=f"{self.base_url}/Chassis/Self/Power"
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            if response.status_code==200:
                if "PowerSupplies" not in response.json():
                    c=response.json()["PowerControl"][0]["PowerMetrics"]["CurConsumedWatts"]
                    a=[]
                    for i in response.json()["Voltages"]:
                        if "PSU" not in i["Name"]:
                            continue
                        if "ReadingVolts" not in i:
                            continue
                        a.append(i["ReadingVolts"])
                    a=sum(a)/len(a)
                    return [[round(a,2),round(c/a,2),round(c,2)]]
                lt=response.json()["PowerSupplies"]
                result=[]
                for i in lt:
                    result.append([i["LineInputVoltage"],round(i["PowerInputWatts"]/i["LineInputVoltage"],2),i["PowerInputWatts"]])
                return result
            url=f"{self.base_url}/Chassis/BMC_0/Power"
            response=self.session.get(
                url,
                verify=False,
                timeout=60
            )
            if response.status_code==200:
                c=response.json()["PowerControl"][0]["PowerMetrics"]["CurConsumedWatts"]
                a=[]
                for i in response.json()["Voltages"]:
                    if "PSU" not in i["Name"]:
                        continue
                    if "ReadingVolts" not in i:
                        continue
                    a.append(i["ReadingVolts"])
                a=sum(a)/len(a)
                return [[round(a,2),round(c/a,2),round(c,2)]]
        except Exception as e:
            logging.error("="*50+"\n"+self.idrac_ip+"\n"+str(e)+"\n"+"="*50)
            return [[0.00,0.00,0.00]]

if __name__=="__main__":
    m=AMI("10.194.25.237","ADMIN","ADMIN@123")
    print(m.get_psu_detail())
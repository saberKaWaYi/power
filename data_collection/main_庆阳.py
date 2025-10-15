import os
import logging
from logging.handlers import RotatingFileHandler
from get_relationship import get_relationship,get_ObjectId
from connect import Connect_Mysql,Connect_Clickhouse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor,as_completed
import requests
import subprocess
from redfish import *
from tool import fc2

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

class Run:

    def __init__(self,config1,config2,config3):
        self.config1=config1
        self.config2=config2
        self.config3=config3
        self.zd1=get_relationship(self.config1,get_ObjectId(self.config1,"庆阳"))
        conn=Connect_Mysql(self.config2)
        self.zd2=conn.get_table_data("power.server_username_and_password","select hostname,username,password from power.server_username_and_password")[["hostname","username","password"]].values.tolist()
        self.zd2=dict(zip([i[0] for i in self.zd2],[(i[1],i[2]) for i in self.zd2]))
        self.time_=datetime.now()
        self.result=[]

    def run(self):
        with ThreadPoolExecutor(max_workers=300) as executor:
            pool=[]
            for i in self.zd1:
                for j in self.zd1[i]:
                    pool.append(executor.submit(self.fc,[i,j]))
            for task in as_completed(pool):
                task.result()
        conn=Connect_Clickhouse(self.config3)
        client=conn.client
        insert_sql="""
        INSERT INTO power.power_data
        (city, data_center, room, rack, hostname, ts, voltage, current, power, ip, brand, type)
        VALUES
        """
        values=[]
        for item in self.result:
            values.append(
                f"('{item['city']}', '{item['data_center']}', '{item['room']}', '{item['rack']}', "
                f"'{item['hostname']}', '{item['ts'].strftime('%Y-%m-%d %H:%M:%S')}', "
                f"{item['voltage']}, {item['current']}, {item['power']}, "
                f"'{item['ip']}', '{item['brand']}', '{item['type']}')"
            )
        insert_sql+=",".join(values)
        client.execute(insert_sql)

    def fc(self,info):
        key=info[0];value=info[1]
        temp_zd={}
        temp_lt=key.split("|")
        temp_zd["city"]=temp_lt[0];temp_zd["data_center"]=temp_lt[1];temp_zd["room"]=temp_lt[2];temp_zd["rack"]=temp_lt[3]
        if value[-1]=="network":
            temp=self.fc1([value[0],value[1],value[2]])
        elif value[-1]=="server":
            temp=self.fc2([value[0],value[1],value[2]])
        else:
            logging.error("="*50+"/n"+f"{value[-1]}未知type。/n"+"="*50)
            return
        temp_zd["hostname"]="-".join([i.strip() for i in value[0].split("-")])
        temp_zd["ts"]=self.time_
        temp_zd["voltage"]=temp[0]
        temp_zd["current"]=temp[1]
        temp_zd["power"]=temp[2]
        temp_zd["ip"]=value[1].strip()
        temp_zd["brand"]=value[2].lower().strip()
        temp_zd["type"]=value[-1]
        self.result.append(temp_zd)

    def fc1(self,info):
        try:
            hostname,ip,brand=info[0].strip(),info[1].strip(),info[2].lower().strip()
            hostname="-".join([i.strip() for i in hostname.split("-")])
            if hostname.lower()=="none" or hostname.lower()=="null" or hostname.lower()=="nan" or hostname=="" or hostname=="-" or hostname=="--" or hostname=="---" or hostname==None:
                return [0.00,0.00,0.00]
            if "." not in ip:
                return [0.00,0.00,0.00]
            if brand=="" or brand=="-" or brand=="--" or brand=="---" or brand=="none" or brand=="null" or brand=="nan" or brand==None:
                return [0.00,0.00,0.00]
            ##################################################
            if brand not in ["huawei","huarong"]:
                return [0.00,0.00,0.00]
            ##################################################
            if brand=="huawei" or brand=="huarong":
                result=[]
                command_list=[" 1.3.6.1.4.1.2011.5.25.31.1.1.18.1.8"," 1.3.6.1.4.1.2011.5.25.31.1.1.18.1.7"," 1.3.6.1.4.1.2011.6.157.1.6"]
                for command in command_list:
                    command="snmpwalk -v 2c -c QAZXSWedc "+ip+command
                    process=subprocess.run(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    temp=[]
                    for line in process.stdout.strip().split("\n"):
                        s=line[line.index(":")+1:].strip().strip("\"")
                        temp.append(eval(s))
                    if int(command[-1])==7:
                        result.append(round(sum(temp),2)/1000)
                        continue
                    result.append(round(sum(temp)/len(temp),2)/1000)
                return result
            result=[]
            url_post='http://10.213.136.111:40061/network_app/distribute_config/exec_cmd/'
            config={
                "device_hostname":hostname,
                "operator":"LCL",
                "is_edit":False,
                "cmd":""
            }
            url_get=f"http://10.216.142.10:40061/network_app/conf/device/data_list/?device_hostname={hostname}"
            response_url_get=requests.get(url_get).json()
            try:
                client_names=response_url_get["data"][0]["net_data"]
            except Exception as e:
                logging.error("="*50+"\n"+"json解析错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
                return [0.00,0.00,0.00]
            if client_names:
                temp=[]
                for client_name in client_names:
                    if client_name["operator"]!="LCL":
                        continue
                    temp.append((client_names[client_name]["client_name"],client_names[client_name]["created_at"]))
                temp.sort(key=lambda x:x[1])
                config["client_name"]=temp[-1][0]
            if brand=="fenghuo":
                config["cmd"]="show power"
                response=requests.post(url_post,json=config)
                data=response.json()["data"]["cmd_result"]
                if not data and "client_name" in config:
                    del config["client_name"]
                    response=requests.post(url_post,json=config)
                    data=response.json()["data"]["cmd_result"]
                temp=data.split("\n")
                for i in temp:
                    if "Power-" not in i:
                        continue
                    temp_temp=i.split()
                    if "*"==temp_temp[0]:
                        temp_temp=temp_temp[1:]
                    a=0 if temp_temp[8]=="N/A" else eval(temp_temp[8])
                    b=0 if temp_temp[9]=="N/A" else eval(temp_temp[9])
                    c=0 if temp_temp[10]=="N/A" else eval(temp_temp[10])
                    result.append([a,b,c])
            elif brand=="nokia":
                return [0.00,0.00,0.00]
                config["cmd"]="show chassis power-supply"
                response=requests.post(url_post,json=config)
                data=response.json()["data"]["cmd_result"]
                if not data and "client_name" in config:
                    del config["client_name"]
                    response=requests.post(url_post,json=config)
                    data=response.json()["data"]["cmd_result"]
                print(data)
            elif brand=="junos":
                config["cmd"]="show chassis environment pem"
                response=requests.post(url_post,json=config)
                data=response.json()["data"]["cmd_result"]
                if not data and "client_name" in config:
                    del config["client_name"]
                    response=requests.post(url_post,json=config)
                    data=response.json()["data"]["cmd_result"]
                temp=data.split("\n")
                for i in range(len(temp)):
                    if "DC Output" not in temp[i]:
                        continue
                    temp_temp=temp[i+1].split()
                    result.append([eval(temp_temp[0]),eval(temp_temp[1]),eval(temp_temp[2])])
            elif brand=="h3c":
                config["cmd"]="display power"
                response=requests.post(url_post,json=config)
                data=response.json()["data"]["cmd_result"]
                if not data and "client_name" in config:
                    del config["client_name"]
                    response=requests.post(url_post,json=config)
                    data=response.json()["data"]["cmd_result"]
                temp=data.split("\n")
                for i in temp:
                    if "Normal" not in i:
                        continue
                    temp_temp=i.split()
                    a=0 if temp_temp[-2]=="--" else eval(temp_temp[-2])
                    b=0 if temp_temp[-3]=="--" else eval(temp_temp[-3])
                    c=0 if temp_temp[-1]=="--" else eval(temp_temp[-1])
                    result.append([a,b,c])
            else:
                logging.error("="*50+"\n"+"未知品牌"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
                return [0.00,0.00,0.00]
            return self.demo(result)
        except Exception as e:
            logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
            return [0.00,0.00,0.00]
    
    def fc2(self,info):
        try:
            hostname,ip,brand=info[0].strip(),info[1].strip(),info[2].lower().strip()
            hostname="-".join([i.strip() for i in hostname.split("-")])
            if hostname.lower()=="none" or hostname.lower()=="null" or hostname.lower()=="nan" or hostname=="" or hostname=="-" or hostname=="--" or hostname=="---" or hostname==None:
                return [0.00,0.00,0.00]
            if "." not in ip:
                return [0.00,0.00,0.00]
            if brand=="" or brand=="-" or brand=="--" or brand=="---" or brand=="none" or brand=="null" or brand=="nan" or brand==None:
                return [0.00,0.00,0.00]
            if ip in ["10.213.33.184","10.213.35.86","10.213.35.87"]:
                try:
                    return fc2(ip,"ADMIN","ADMIN@123")[0]
                except Exception as e:
                    logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
                    return [0.00,0.00,0.00]
            if hostname not in self.zd2:
                return [0.00,0.00,0.00]
            username=self.zd2[hostname][0];password=self.zd2[hostname][1]
            if brand=="supermicro":
                try:
                    lt=[]
                    for i in range(3,6):
                        command=f"snmpwalk -v 2c -c public {ip} iso.3.6.1.4.1.21317.1.14.2.1.{i}"
                        process=subprocess.run(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        temp=[]
                        for line in process.stdout.strip().split("\n"):
                            s=line[line.index(":")+1:].strip().strip("\"")
                            temp.append(eval(s))
                        lt.append(temp)
                    result=[]
                    for i in range(len(lt[0])):
                        temp=[]
                        for j in range(3):
                            temp.append(lt[j][i])
                        result.append(temp)
                    return self.demo(result)
                except:
                    try:
                        m=Supermicro(ip,username,password)
                        return self.demo(m.get_psu_detail())
                    except Exception as e:
                        logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
            elif brand=="dell inc.":
                try:
                    m=Dell(ip,username,password)
                    return self.demo(m.get_psu_detail())
                except Exception as e:
                    logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
            elif brand=="inspur":
                try:
                    m=Inspur(ip,username,password)
                    return self.demo(m.get_psu_detail())
                except Exception as e:
                    logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
            elif brand=="xfusion":
                try:
                    m=Xfusion(ip,username,password)
                    return self.demo(m.get_psu_detail())
                except Exception as e:
                    logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
            elif brand=="ami":
                try:
                    m=AMI(ip,username,password)
                    return self.demo(m.get_psu_detail())
                except Exception as e:
                    logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
            else:
                logging.error("="*50+"\n"+"未知品牌"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+"="*50)
            return [0.00,0.00,0.00]
        except Exception as e:
            logging.error("="*50+"\n"+"未知错误"+"\n"+hostname+"\n"+ip+"\n"+brand+"\n"+str(e)+"\n"+"="*50)
            return [0.00,0.00,0.00]

    def demo(self,lt):
        c=sum([i[2] for i in lt])
        if c==0:
            return [0.00,0.00,0.00]
        b=sum([i[1] for i in lt])
        a=sum([i[0]*i[2] for i in lt])/c
        return [round(a,2),round(b,2),round(c,2)]

if __name__=="__main__":
    config1={
        "connection":{
            "TIMES":1000,
            "TIME":0.1
        },
        "mongodb":{
            "HOST":"10.216.141.46",
            "PORT":27017,
            "USERNAME":"manager",
            "PASSWORD":"cds-cloud@2017"
        }
    }
    config2={
        "connection":{
            "TIMES":1000,
            "TIME":0.1
        },
        "mysql":{
            "HOST":"10.216.141.30",
            "PORT":19002,
            "USERNAME":"devops_master",
            "PASSWORD":"cds-cloud@2017"
        }
    }
    config3={
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
    m=Run(config1,config2,config3)
    m.run()
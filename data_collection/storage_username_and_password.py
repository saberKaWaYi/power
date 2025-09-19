from get_relationship import get_relationship,get_ObjectId
from concurrent.futures import ThreadPoolExecutor,as_completed
from redfish import *
from connect import Connect_Mysql

class Run:

    def __init__(self,config1,config2):
        self.config=config2
        zd=get_relationship(config1,get_ObjectId(config1,"庆阳"))
        self.zd={}
        for i in zd:
            for j in zd[i]:
                if j[-1]=="server":
                    if j[-2] not in self.zd:
                        self.zd[j[-2]]=[]
                    self.zd[j[-2]].append([j[0],j[1],j[2]])
        self.result=[]

    def run(self):
        with ThreadPoolExecutor(max_workers=50) as executor:
            pool=[]
            for i in self.zd:
                for j in self.zd[i]:
                    pool.append(executor.submit(self.fc,j))
            for task in as_completed(pool):
                task.result()
        conn=Connect_Mysql(self.config)
        cursor=conn.client.cursor()
        insert_sql="""
        INSERT INTO power.server_username_and_password 
        (hostname, idrac_ip, brand, username, password) 
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            idrac_ip = VALUES(idrac_ip),
            brand = VALUES(brand),
            username = VALUES(username),
            password = VALUES(password)
        """
        cursor.executemany(insert_sql,self.result)
        conn.client.commit()

    def fc(self,info):
        hostname,ip,brand=info[0].strip(),info[1].strip(),info[2].lower().strip()
        hostname="-".join([i.strip() for i in hostname.split("-")])
        if hostname.lower()=="none" or hostname.lower()=="null" or hostname.lower()=="nan" or hostname=="" or hostname=="-" or hostname=="--" or hostname=="---" or hostname==None:
            return
        if "." not in ip:
            return
        if brand=="" or brand=="-" or brand=="--" or brand=="---" or brand=="none" or brand=="null" or brand=="nan" or brand==None:
            return
        ##################################################
        if brand!="ami":
            return
        ##################################################
        if brand=="supermicro":
            m=Supermicro(ip,"ADMIN","ADMIN@123")
            if m.error_reason:
                return
            self.result.append([hostname,ip,brand,"ADMIN","ADMIN@123"])
        elif brand=="dell inc.":
            m=Dell(ip,"root","P@$$w0rd")
            if m.error_reason:
                pass
            else:
                self.result.append([hostname,ip,brand,"root","P@$$w0rd"])
                return
            m=Dell(ip,"root","calvin")
            if m.error_reason:
                return
            self.result.append([hostname,ip,brand,"root","calvin"])
        elif brand=="inspur":
            m=Inspur(ip,"admin","P@$$w0rd")
            if m.error_reason:
                pass
            else:
                self.result.append([hostname,ip,brand,"admin","P@$$w0rd"])
                return
            m=Inspur(ip,"admin","admin")
            if m.error_reason:
                return
            self.result.append([hostname,ip,brand,"admin","admin"])
        elif brand=="xfusion":
            m=Xfusion(ip,"ADMIN","ADMIN@123")
            if m.error_reason:
                return
            self.result.append([hostname,ip,brand,"ADMIN","ADMIN@123"])
        elif brand=="ami":
            # AMI有一台尚待解决
            m=AMI(ip,"ADMIN","ADMIN@123")
            if m.error_reason:
                return
            self.result.append([hostname,ip,brand,"ADMIN","ADMIN@123"])

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
    m=Run(config1,config2)
    m.run()
# 这个脚本有点问题，须按品牌区分来跑
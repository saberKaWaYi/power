from connect import Connect_Clickhouse

if __name__=="__main__":
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
    conn=Connect_Clickhouse(config)
    data=conn.query("SELECT * FROM power.power_data limit 1")
    print(data)
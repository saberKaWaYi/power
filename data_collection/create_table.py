from connect import Connect_Clickhouse

def create_table(config):
    conn=Connect_Clickhouse(config)
    client=conn.client
    create_sql="CREATE DATABASE IF NOT EXISTS power"
    client.execute(create_sql)
    create_sql="""
    CREATE TABLE IF NOT EXISTS power.power_data
    (
        city        String,      -- 城市
        data_center String,      -- 数据中心
        room        String,      -- 机房
        rack        String,      -- 机柜
        hostname    String,      -- 主机名
        ts          DateTime,    -- 收集时间
        voltage     Float32,     -- 电压 (V)
        current     Float32,     -- 电流 (A)
        power       Float32      -- 功率 (W)
    )
    ENGINE = MergeTree
    PARTITION BY toYYYYMMDD(ts)
    ORDER BY (city, data_center, room, rack, hostname, ts)
    """
    client.execute(create_sql)
    print("power_data 表创建完成！")

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
    create_table(config)
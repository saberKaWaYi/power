FROM dockerhub.capitalonline.net/devops_project/migrate_center:v3.3

WORKDIR /app

COPY . /app

RUN pip install Django==5.2 djangorestframework==3.16.0 clickhouse-driver pymongo==3.12.0 pandas pymysql requests==2.32.4 kafka-python -i https://mirrors.aliyun.com/pypi/simple

EXPOSE 8000

WORKDIR /app/project

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
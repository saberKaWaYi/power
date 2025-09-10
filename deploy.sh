git pull origin master

docker rm -f django_app 2>/dev/null || true

docker compose up -d --build

echo "Django 服务已启动。"
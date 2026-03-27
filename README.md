###更新代码后重新构建容器
docker compose build --no-cache api worker frontend admin 
docker compose up -d api worker frontend admin
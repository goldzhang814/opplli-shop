###更新代码后重新构建容器
docker compose build --no-cache api worker frontend admin 
docker compose up -d api worker frontend admin

###重启数据库
pkill -f /usr/local/mysql/bin/mysqld

#### 或更安全：
/usr/local/mysql/bin/mysqladmin -uroot -p shutdown

#### 启动
/usr/local/mysql/bin/mysqld_safe --user=mysql &
默认账号密码是：
字段值邮箱:admin@example.com
密码:changeme123

后端启动指南
方式一：Docker（推荐，一键启动全部服务）
bash# 1. 进入项目根目录
cd ecom

# 2. 复制环境变量
cp .env.example .env

# 3. 编辑 .env，填入必要配置（至少填这几个）
nano .env

# 4. 一键启动所有服务
docker compose up -d

# 5. 等待 MySQL 就绪后跑数据库迁移
docker compose exec api alembic upgrade head

# 6. 查看日志
docker compose logs -f api


方式一补充：只部署 backend 容器（MySQL/Redis 在宿主机）
cd ecom/backend

# 1. 复制环境变量
cp .env.docker.example .env

# 2. 编辑 .env，把密码等敏感值改掉
nano .env

# 3. 构建并启动 backend（宿主机端口 9010 -> 容器 8000）
docker compose up -d --build

# 4. 运行数据库迁移（确保宿主机 MySQL 已启动）
docker compose exec api alembic upgrade head


方式二：本地开发（不用 Docker）
cd ecom/backend

# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 复制并配置环境变量
cp ../.env.example .env
nano .env                         # 填入数据库连接等

# 4. 跑数据库迁移（建表 + 种子数据）
alembic upgrade head

# 5. 启动 API 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. 另开终端，启动 Celery Worker（处理邮件等异步任务）
celery -A app.core.celery_app worker --loglevel=info

# 7. 另开终端，启动 Celery Beat（定时任务，如关闭过期横幅）
celery -A app.core.celery_app beat --loglevel=info

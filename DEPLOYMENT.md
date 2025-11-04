# 部署文档

## 服务器要求

### 最低配置
- CPU: 2核
- 内存: 4GB
- 磁盘: 20GB
- 操作系统: Ubuntu 20.04+ / CentOS 7+ / Windows Server 2016+

### 推荐配置
- CPU: 4核
- 内存: 8GB
- 磁盘: 50GB SSD
- 操作系统: Ubuntu 22.04 LTS

## 部署步骤（Linux）

### 1. 安装系统依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3 和 pip
sudo apt install python3 python3-pip python3-venv -y

# 安装 Nginx
sudo apt install nginx -y

# 安装其他依赖
sudo apt install git -y
```

### 2. 创建应用用户

```bash
sudo useradd -m -s /bin/bash c45app
sudo su - c45app
```

### 3. 克隆项目

```bash
cd /home/c45app
git clone <repository-url> c4.5
cd c4.5
```

### 4. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 6. 配置环境变量

```bash
# 创建环境变量文件
cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
EOF

# 加载环境变量
source .env
```

### 7. 创建必要目录

```bash
mkdir -p logs uploads
chmod 755 logs uploads
```

### 8. 测试运行

```bash
gunicorn -c gunicorn_config.py app:app
```

访问 `http://服务器IP:5000` 测试是否正常。

### 9. 配置 Systemd 服务

退出应用用户，回到 root：

```bash
exit  # 退出 c45app 用户
```

创建服务文件：

```bash
sudo nano /etc/systemd/system/c45-web.service
```

添加以下内容：

```ini
[Unit]
Description=C4.5 Web Application
After=network.target

[Service]
Type=notify
User=c45app
Group=c45app
WorkingDirectory=/home/c45app/c4.5
Environment="PATH=/home/c45app/c4.5/venv/bin"
EnvironmentFile=/home/c45app/c4.5/.env
ExecStart=/home/c45app/c4.5/venv/bin/gunicorn -c gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start c45-web
sudo systemctl enable c45-web
sudo systemctl status c45-web
```

### 10. 配置 Nginx 反向代理

创建 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/c45-web
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或IP

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /static/ {
        alias /home/c45app/c4.5/static/;
        expires 30d;
    }

    access_log /var/log/nginx/c45-web-access.log;
    error_log /var/log/nginx/c45-web-error.log;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/c45-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 11. 配置 HTTPS（推荐）

安装 Certbot：

```bash
sudo apt install certbot python3-certbot-nginx -y
```

获取证书：

```bash
sudo certbot --nginx -d your-domain.com
```

Certbot 会自动配置 HTTPS 并设置自动续期。

### 12. 配置定时清理任务

```bash
sudo su - c45app
crontab -e
```

添加以下行：

```cron
# 每小时清理过期文件
0 * * * * cd /home/c45app/c4.5 && /home/c45app/c4.5/venv/bin/python scripts/cleanup_old_files.py >> logs/cleanup.log 2>&1
```

## 部署步骤（Windows）

### 1. 安装 Python

从 https://www.python.org/downloads/ 下载并安装 Python 3.9+

### 2. 安装依赖

```cmd
cd C:\path\to\c4.5
pip install -r requirements.txt
pip install waitress
```

### 3. 创建启动脚本

创建 `start.bat`：

```batch
@echo off
set SECRET_KEY=your-secret-key-here
set FLASK_ENV=production
waitress-serve --port=5000 app:app
```

### 4. 配置 Windows 服务

使用 NSSM (Non-Sucking Service Manager)：

1. 下载 NSSM: https://nssm.cc/download
2. 安装服务：

```cmd
nssm install C45Web "C:\Python39\python.exe" "-m waitress --port=5000 app:app"
nssm set C45Web AppDirectory "C:\path\to\c4.5"
nssm start C45Web
```

### 5. 配置 IIS 反向代理（可选）

安装 URL Rewrite 和 Application Request Routing 模块后，配置 web.config。

## 监控和维护

### 查看日志

```bash
# 应用日志
tail -f logs/error.log
tail -f logs/access.log

# 清理日志
tail -f logs/cleanup.log

# 系统服务日志
sudo journalctl -u c45-web -f
```

### 重启服务

```bash
sudo systemctl restart c45-web
```

### 更新应用

```bash
sudo su - c45app
cd /home/c45app/c4.5
git pull
source venv/bin/activate
pip install -r requirements.txt
exit

sudo systemctl restart c45-web
```

### 监控磁盘使用

```bash
# 检查 uploads 目录大小
du -sh /home/c45app/c4.5/uploads

# 如果过大，手动清理
sudo -u c45app python3 /home/c45app/c4.5/scripts/cleanup_old_files.py
```

## 安全加固

### 防火墙配置

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 限制上传

在 Nginx 配置中已设置：
```nginx
client_max_body_size 10M;
```

### 定期备份

创建备份脚本 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/backup/c45"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/c45_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='uploads' \
    --exclude='*.pyc' \
    /home/c45app/c4.5

# 删除7天前的备份
find $BACKUP_DIR -name "c45_*.tar.gz" -mtime +7 -delete
```

配置每日备份：

```bash
sudo crontab -e

# 每天凌晨3点备份
0 3 * * * /home/c45app/backup.sh
```

## 故障排除

### 服务无法启动

```bash
# 检查服务状态
sudo systemctl status c45-web

# 查看详细日志
sudo journalctl -u c45-web -n 100

# 检查配置文件
/home/c45app/c4.5/venv/bin/python -m py_compile app.py
```

### 文件上传失败

- 检查 `uploads/` 目录权限
- 确认 Nginx 配置的 `client_max_body_size`
- 查看磁盘空间是否充足

### 性能问题

- 增加 Gunicorn workers 数量
- 升级服务器配置
- 使用 Redis 存储会话数据

## 联系方式

如有部署问题，请联系技术支持或查阅项目文档。

"""
Gunicorn 配置文件
"""
import multiprocessing

# 绑定地址和端口
bind = "0.0.0.0:5000"

# Worker 进程数
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型
worker_class = "sync"

# 每个 worker 的线程数
threads = 2

# 超时时间（秒）
timeout = 120

# 保持活动连接
keepalive = 5

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 守护进程
daemon = False

# PID 文件
pidfile = "logs/gunicorn.pid"

# 优雅重启超时
graceful_timeout = 30

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

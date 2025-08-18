# Gunicorn configuration for production deployment
import multiprocessing

# Server socket
bind = "127.0.0.1:5001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for large file processing
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/converter-app/access.log"
errorlog = "/var/log/converter-app/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "converter-app"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# File upload limits
max_requests_jitter = 50

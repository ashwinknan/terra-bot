# File: backend/gunicorn_config.py
import os
import multiprocessing

# Basic config
port = int(os.environ.get('PORT', '10000'))
bind = f"0.0.0.0:{port}"

# Worker Settings
workers = 1
worker_class = 'sync'
threads = 4  # Increased from 1
max_requests = 0
max_requests_jitter = 0

# Increase timeouts
timeout = 300  # 5 minutes
graceful_timeout = 120
keepalive = 5

# Request Settings
max_requests = 0  # Disable max requests
max_requests_jitter = 0

# Server Mechanics
preload_app = True  # Enable preloading
daemon = False
reload = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

# Startup and Shutdown Hooks
def on_starting(server):
    server.log.info("Starting Gunicorn Server")

def on_exit(server):
    server.log.info("Shutting down Gunicorn Server")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_exit(server, worker):
    server.log.info(f"Worker exited (pid: {worker.pid})")
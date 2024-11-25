# backend/gunicorn_config.py
import multiprocessing
import os

# Basic config
bind = f"0.0.0.0:{os.getenv('PORT', '5001')}"
worker_class = 'gthread'
workers = 1
threads = 4

# Timeouts and limits
timeout = 120
keepalive = 5
max_requests = 100
max_requests_jitter = 20
graceful_timeout = 30

# Performance optimizations
worker_tmp_dir = "/dev/shm"
preload_app = True
daemon = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'

# Process naming
proc_name = 'rag-game-assistant'

def post_fork(server, worker):
    """Setup after worker fork"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_int(worker):
    """Worker shutdown on SIGINT"""
    worker.log.info(f"Worker shutting down: {worker.pid}")

def worker_abort(worker):
    """Worker shutdown on SIGABRT"""
    worker.log.info(f"Worker aborting: {worker.pid}")
# File: backend/gunicorn_config.py
import os

# Basic config
port = int(os.environ.get('PORT', '10000'))
bind = f"0.0.0.0:{port}"
worker_class = 'gthread'
workers = 1  # Keep single worker for consistent state
threads = 4

# Increase timeouts
timeout = 300  # Increased to 5 minutes
keepalive = 5
max_requests = 100
max_requests_jitter = 20
graceful_timeout = 60

# Performance optimizations
worker_tmp_dir = "/dev/shm"
preload_app = False  # Changed to False to prevent memory issues
daemon = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'rag-game-assistant'

def on_starting(server):
    """Log when server starts"""
    server.log.info("Gunicorn server is starting")

def when_ready(server):
    """Log when server is ready"""
    server.log.info("Gunicorn server is ready!")

def post_fork(server, worker):
    """Setup after worker fork"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_int(worker):
    """Worker shutdown on SIGINT"""
    worker.log.info(f"Worker shutting down: {worker.pid}")

def worker_abort(worker):
    """Worker shutdown on SIGABRT"""
    worker.log.info(f"Worker aborting: {worker.pid}")
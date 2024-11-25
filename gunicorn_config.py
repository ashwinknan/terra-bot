# backend/gunicorn_config.py

import multiprocessing
import os

# Bind to PORT provided by Render
bind = f"0.0.0.0:{os.getenv('PORT', '5001')}"

# Worker configuration
worker_class = 'gthread'  # Use threads
workers = 2  # Number of worker processes
threads = 4  # Threads per worker
timeout = 300  # Worker timeout in seconds

# Request handling
max_requests = 1000
max_requests_jitter = 50
backlog = 100
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# SSL Configuration (if needed)
keyfile = None
certfile = None

def on_starting(server):
    """Run when server starts"""
    print("Gunicorn server is starting")

def on_exit(server):
    """Run when server exits"""
    print("Gunicorn server is shutting down")

def post_worker_init(worker):
    """Run after worker process is initialized"""
    print(f"Initializing worker {worker.pid}")

def worker_exit(server, worker):
    """Run when a worker exits"""
    print(f"Worker {worker.pid} exited")
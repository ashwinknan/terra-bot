# File: backend/gunicorn_config.py
import os
import multiprocessing

# Basic config
port = int(os.environ.get('PORT', '10000'))
bind = f"0.0.0.0:{port}"

# Worker Settings
workers = 1  # Single worker to prevent memory issues
worker_class = 'sync'  # Changed from gthread to sync
threads = 1  # Reduced threads to prevent concurrency issues

# Timeouts
timeout = 600  # 10 minutes
graceful_timeout = 300  # 5 minutes
keepalive = 2

# Request Settings
max_requests = 0  # Disable max requests
max_requests_jitter = 0

# Server Mechanics
preload_app = False
daemon = False
reload = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

def on_starting(server):
    server.log.info("Starting Gunicorn Server")

def on_exit(server):
    server.log.info("Shutting down Gunicorn Server")
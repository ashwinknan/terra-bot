import os
import sys
from pathlib import Path

# Add the backend directory to Python path
current_dir = Path(__file__).parent.resolve()
backend_path = current_dir / "backend"
sys.path.insert(0, str(backend_path))

import subprocess
import time
import requests
import signal
import yaml
from dotenv import load_dotenv
from threading import Thread
import logging

# Now import app-related modules after path is set
from app.core.initializer import AppComponents
from app.main import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_section(title):
    logger.info(f"\n{'='*20} {title} {'='*20}")

def load_env_file():
    """Load environment variables from .env file"""
    env_path = backend_path / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✓ Loaded environment variables from {env_path}")
        return True
    else:
        logger.error(f"ERROR: .env file not found at {env_path}")
        return False

def run_command(command, cwd=None, timeout=30):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def test_installation():
    """Test pip installation and dependency conflicts"""
    print_section("Testing Installation")
    
    # First test pip itself
    success, output = run_command("pip --version")
    assert success, "pip is not installed or not working"
        
    # Test requirements installation
    success, output = run_command("pip install -r requirements.txt", cwd=str(backend_path))
    assert success, f"Installation failed: {output}"
        
    # Check for dependency conflicts
    success, output = run_command("pip check", cwd=str(backend_path))
    assert success, f"Dependency conflicts found: {output}"
        
    logger.info("✓ Package installation and dependency check successful")

def test_imports():
    """Test if all required packages can be imported"""
    print_section("Testing Imports")
    required_packages = [
        'flask',
        'langchain',
        'chromadb',
        'anthropic',
        'cohere',
        'gunicorn'
    ]
    
    failed_imports = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError as e:
            failed_imports.append(f"{package}: {str(e)}")
    
    assert not failed_imports, "\n".join(failed_imports)
    logger.info("✓ All required packages imported successfully")

def test_render_yaml():
    """Validate render.yaml configuration"""
    print_section("Testing Render Configuration")
    render_yaml_path = current_dir / "render.yaml"
    
    assert render_yaml_path.exists(), "render.yaml not found"
    
    try:
        with open(render_yaml_path) as f:
            config = yaml.safe_load(f)
            
        # Validate required fields
        required_fields = ['services']
        for field in required_fields:
            assert field in config, f"Missing required field in render.yaml: {field}"
        
        # Validate service configuration
        service = config['services'][0]
        required_service_fields = ['type', 'name', 'env', 'buildCommand', 'startCommand']
        for field in required_service_fields:
            assert field in service, f"Missing required service field: {field}"
        
        # Validate environment variables
        if 'envVars' in service:
            required_env_vars = ['ANTHROPIC_API_KEY', 'COHERE_API_KEY']
            defined_vars = [env['key'] for env in service['envVars']]
            for var in required_env_vars:
                assert var in defined_vars, f"Missing required environment variable in render.yaml: {var}"
        
        logger.info("✓ render.yaml is valid")
        
    except yaml.YAMLError as e:
        assert False, f"Error parsing render.yaml: {str(e)}"
    except Exception as e:
        assert False, f"Error validating render.yaml: {str(e)}"

def test_gunicorn():
    """Test if gunicorn can start the app"""
    print_section("Testing Gunicorn")
    process = None
    
    try:
        # Ensure port is free
        try:
            for cmd in ["lsof -ti:5001", "pkill -f gunicorn", "pkill -f flask"]:
                subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)  # Give more time for cleanup
        except:
            pass

        # Create test config
        config_content = f"""
import multiprocessing
import sys
import os

# Add backend path
sys.path.insert(0, "{str(backend_path)}")

# Server config
bind = "127.0.0.1:5001"  # Changed to localhost explicitly
workers = 1
threads = 1
worker_class = "sync"
timeout = 120
keepalive = 2
max_requests = 0
proc_name = "rag-game-assistant"
preload_app = False  # Changed to False to prevent double initialization
reload = False
daemon = False
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "debug"

def when_ready(server):
    print("Gunicorn server is ready!")
"""
        config_path = backend_path / "gunicorn_config.py"
        config_path.write_text(config_content)
        
        logger.info("Starting gunicorn...")
        
        # Start gunicorn with proper env vars
        env = os.environ.copy()
        env["PYTHONPATH"] = str(backend_path)
        env["ENV"] = "test"
        
        # Start server with initialization logging
        process = subprocess.Popen(
            ["gunicorn", "--config", str(config_path), "wsgi:app"],
            cwd=str(backend_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor server output for readiness
        ready = False
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        
        while time.time() - start_time < timeout and not ready:
            output = process.stdout.readline()
            if output:
                logger.info(f"Server output: {output.strip()}")
                if "Listening at: http://127.0.0.1:5001" in output:
                    ready = True
                    break
            
            error = process.stderr.readline()
            if error:
                logger.error(f"Server error: {error.strip()}")
            
            if process.poll() is not None:
                # Server process ended
                out, err = process.communicate()
                if out:
                    logger.error(f"Final output: {out}")
                if err:
                    logger.error(f"Final error: {err}")
                raise RuntimeError("Server failed to start")
                
            time.sleep(0.1)
            
        if not ready:
            raise TimeoutError("Server failed to start within timeout")
        
        # Test server
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.get("http://127.0.0.1:5001/api/", timeout=5)
                assert response.status_code == 200
                logger.info(f"Server is up! Response: {response.json()}")
                return
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise RuntimeError(f"Failed to connect to server after {max_retries} attempts") from last_error
                
    except Exception as e:
        logger.error(f"Gunicorn test failed: {str(e)}")
        if process:
            out, err = process.communicate()
            if out:
                logger.error(f"Process output: {out}")
            if err:
                logger.error(f"Process error: {err}")
        raise
        
    finally:
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        try:
            if config_path.exists():
                config_path.unlink()
                logger.info("Removed config file")
        except Exception as e:
            logger.warning(f"Could not remove config file: {e}")

def test_api_endpoints():
    """Test critical API endpoints"""
    print_section("Testing API Endpoints")
    
    try:
        # Initialize app with QA chain
        app = create_app(force_recreate=True)  # Force recreate to ensure initialization
        
        # Wait for initialization
        max_wait = 30
        start = time.time()
        while time.time() - start < max_wait:
            try:
                if (hasattr(AppComponents, 'qa_chain_manager') and 
                    AppComponents.qa_chain_manager is not None and
                    hasattr(AppComponents, 'qa_chain') and
                    AppComponents.qa_chain is not None):
                    break
                time.sleep(1)
            except Exception:
                time.sleep(1)
        
        if not (AppComponents.qa_chain_manager and AppComponents.qa_chain):
            raise TimeoutError("QA chain failed to initialize")
            
        with app.test_client() as client:
            # Test health check first
            response = client.get('/api/')
            assert response.status_code == 200
            logger.info("✓ /api/ - Status: 200")
            
            # Test QA endpoint
            response = client.post(
                '/api/ask',
                json={"question": "What is T#?"},
                content_type='application/json'
            )
            
            assert response.status_code == 200, \
                f"QA endpoint returned {response.status_code}: {response.get_json()}"
            logger.info("✓ /api/ask - Status: 200")
            
            # Verify response format
            data = response.get_json()
            assert 'answer' in data
            assert 'sources' in data
            assert len(data['answer']) > 0
            
    except Exception as e:
        logger.error(f"API endpoints test failed: {str(e)}")
        raise
    finally:
        # Cleanup
        try:
            if hasattr(AppComponents, 'vector_store_manager'):
                AppComponents.vector_store_manager.cleanup_all()
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

def main():
    """Run all deployment tests"""
    logger.info("Starting deployment tests...")
    
    tests = [
        ("Installation", test_installation),
        ("Imports", test_imports),
        ("Render Configuration", test_render_yaml),
        ("Gunicorn", test_gunicorn),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            results.append(True)
            logger.info(f"✓ {test_name} test passed")
        except Exception as e:
            logger.error(f"✗ {test_name} test failed: {str(e)}")
            results.append(False)
    
    return all(results)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        sys.exit(1)
        
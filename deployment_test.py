import os
import sys
import subprocess
import time
import requests
import signal
import yaml
from pathlib import Path
from dotenv import load_dotenv
from threading import Thread
import logging

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
    env_path = Path("backend") / ".env"
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
    if not success:
        logger.error("pip is not installed or not working")
        return False
        
    # Test requirements installation
    success, output = run_command("pip install -r requirements.txt", cwd="backend")
    if not success:
        logger.error(f"Installation failed: {output}")
        return False
        
    # Check for dependency conflicts
    success, output = run_command("pip check", cwd="backend")
    if not success:
        logger.error(f"Dependency conflicts found: {output}")
        return False
        
    logger.info("✓ Package installation and dependency check successful")
    return True

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
    
    if failed_imports:
        for failure in failed_imports:
            logger.error(f"Import failed: {failure}")
        return False
        
    logger.info("✓ All required packages imported successfully")
    return True

def test_render_yaml():
    """Validate render.yaml configuration"""
    print_section("Testing Render Configuration")
    render_yaml_path = Path("render.yaml")
    
    if not render_yaml_path.exists():
        logger.error("render.yaml not found")
        return False
    
    try:
        with open(render_yaml_path) as f:
            config = yaml.safe_load(f)
            
        # Validate required fields
        required_fields = ['services']
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field in render.yaml: {field}")
                return False
        
        # Validate service configuration
        service = config['services'][0]
        required_service_fields = ['type', 'name', 'env', 'buildCommand', 'startCommand']
        for field in required_service_fields:
            if field not in service:
                logger.error(f"Missing required service field: {field}")
                return False
        
        # Validate environment variables
        if 'envVars' in service:
            required_env_vars = ['ANTHROPIC_API_KEY', 'COHERE_API_KEY']
            defined_vars = [env['key'] for env in service['envVars']]
            for var in required_env_vars:
                if var not in defined_vars:
                    logger.error(f"Missing required environment variable in render.yaml: {var}")
                    return False
        
        logger.info("✓ render.yaml is valid")
        return True
        
    except yaml.YAMLError as e:
        logger.error(f"Error parsing render.yaml: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error validating render.yaml: {str(e)}")
        return False

def test_gunicorn():
    """Test if gunicorn can start the app"""
    print_section("Testing Gunicorn")
    process = None
    
    try:
        # Ensure port is free
        try:
            subprocess.run(["lsof", "-ti:5001"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["pkill", "-f", "gunicorn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
        except:
            pass

        # Create test config
        backend_path = str(Path("backend").absolute())
        config_content = f"""
import multiprocessing
import sys

sys.path.insert(0, "{backend_path}")

bind = "0.0.0.0:5001"
workers = 1
threads = 4
worker_class = "gthread"
timeout = 120
keepalive = 2
max_requests = 0
proc_name = "rag-game-assistant"
preload_app = True

def when_ready(server):
    print("Gunicorn server is ready!")
"""
        config_path = Path("backend") / "gunicorn_config.py"
        config_path.write_text(config_content)
        
        logger.info("Starting gunicorn...")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = backend_path
        env["GUNICORN_CMD_ARGS"] = "--preload"
        
        process = subprocess.Popen(
            ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"],
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )
        
        def print_output():
            while True:
                if process.poll() is not None:
                    break
                output = process.stdout.readline()
                if output:
                    logger.info(f"Server output: {output.strip()}")
                error = process.stderr.readline()
                if error:
                    logger.error(f"Server error: {error.strip()}")

        output_thread = Thread(target=print_output, daemon=True)
        output_thread.start()

        logger.info("Waiting for server to start...")
        time.sleep(10)
        
        success = False
        start_time = time.time()
        timeout = 60
        
        while time.time() - start_time < timeout:
            try:
                logger.info("Attempting to connect to server...")
                response = requests.get("http://localhost:5001/api/", timeout=5)
                
                if response.status_code == 200:
                    logger.info(f"✓ Server responded successfully with status {response.status_code}")
                    logger.info(f"Response: {response.json()}")
                    success = True
                    break
                else:
                    logger.error(f"Server returned status {response.status_code}")
                
            except requests.ConnectionError as e:
                logger.warning(f"Connection failed, retrying... ({str(e)})")
            except Exception as e:
                logger.error(f"Error during connection attempt: {str(e)}")
            
            time.sleep(2)
            
        if not success:
            logger.error("Server failed to respond within timeout period")
            return False
                
        return success

    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False
        
    finally:
        try:
            if process and process.poll() is None:
                logger.info("Stopping gunicorn...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Force killing process...")
                    process.kill()
                    try:
                        process.wait(timeout=5)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error stopping gunicorn: {e}")
            
        try:
            subprocess.run(["pkill", "-f", "gunicorn"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        except:
            pass
            
        try:
            config_path = Path("backend") / "gunicorn_config.py"
            if config_path.exists():
                config_path.unlink()
                logger.info("Removed config file")
        except Exception as e:
            logger.warning(f"Could not remove config file: {e}")

def test_api_endpoints():
    """Test critical API endpoints"""
    print_section("Testing API Endpoints")
    
    endpoints = [
        {
            "url": "http://localhost:5001/api/",
            "method": "GET",
            "expected_status": 200
        },
        {
            "url": "http://localhost:5001/api/ask",
            "method": "POST",
            "data": {"question": "What is T#?"},
            "expected_status": 200
        }
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"], timeout=5)
            else:
                response = requests.post(endpoint["url"], json=endpoint["data"], timeout=30)
                
            if response.status_code == endpoint["expected_status"]:
                logger.info(f"✓ {endpoint['url']} - Status: {response.status_code}")
            else:
                logger.error(f"✗ {endpoint['url']} - Expected: {endpoint['expected_status']}, Got: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing {endpoint['url']}: {str(e)}")
            return False
            
    return True

def main():
    """Run all deployment tests"""
    logger.info("Starting deployment tests...")
    
    if not load_env_file():
        return False
    
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
            logger.info(f"\nRunning {test_name} test...")
            result = test_func()
            results.append(result)
            if not result:
                logger.error(f"✗ {test_name} test failed")
            else:
                logger.info(f"✓ {test_name} test passed")
        except Exception as e:
            logger.error(f"✗ {test_name} test failed with error: {str(e)}")
            results.append(False)
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("Deployment Test Summary")
    logger.info("="*50)
    logger.info(f"Total Tests: {len(tests)}")
    logger.info(f"Passed: {sum(results)}")
    logger.info(f"Failed: {len(results) - sum(results)}")
    
    # List failed tests
    if not all(results):
        logger.info("\nFailed Tests:")
        for (test_name, _), result in zip(tests, results):
            if not result:
                logger.info(f"- {test_name}")
    
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
import os
import sys
import subprocess
import platform
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

def print_section(title):
    print(f"\n{'='*20} {title} {'='*20}")

def load_env_file():
    """Load environment variables from .env file in backend directory"""
    backend_dir = Path("backend")
    env_path = backend_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment variables from {env_path}")
    else:
        print(f"ERROR: .env file not found at {env_path}")

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def test_environment():
    """Test Python environment and dependencies"""
    print_section("Testing Environment")
    
    # Check Python version
    print(f"Python Version: {platform.python_version()}")
    
    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    print(f"Running in virtual environment: {in_venv}")
    if not in_venv:
        print("WARNING: It's recommended to run this in a virtual environment")
    return True

def test_installation():
    """Test the installation process"""
    print_section("Testing Installation")
    
    # Verify backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("ERROR: 'backend' directory not found")
        return False
        
    # Test pip install
    success, output = run_command("pip install -r requirements.txt", cwd="backend")
    if not success:
        print("ERROR: Failed to install requirements")
        print(output)
        return False
    print("✓ Requirements installed successfully")
    return True

def test_application_startup():
    """Test the application startup"""
    print_section("Testing Application Startup")
    
    # Check if gunicorn is installed
    success, _ = run_command("gunicorn --version", cwd="backend")
    if not success:
        print("ERROR: gunicorn not found. Installing...")
        success, output = run_command("pip install gunicorn", cwd="backend")
        if not success:
            print("ERROR: Failed to install gunicorn")
            print(output)
            return False
    
    # Start the application in the background
    print("Starting application...")
    process = subprocess.Popen(
        "gunicorn 'app:create_app()' --bind 0.0.0.0:5001",
        shell=True,
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the application to start
    time.sleep(5)
    
    # Test if the application is responding
    try:
        response = requests.post(
            "http://localhost:5001/api/ask",
            json={"question": "test question"}
        )
        if response.status_code == 200:
            print("✓ Application started and responding")
            success = True
        else:
            print(f"ERROR: Application returned status code {response.status_code}")
            success = False
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to application")
        success = False
    
    # Clean up
    process.terminate()
    process.wait()
    
    return success

def verify_environment_variables():
    """Verify required environment variables"""
    print_section("Checking Environment Variables")
    
    required_vars = [
        "ANTHROPIC_API_KEY",
        "COHERE_API_KEY",
        "ALLOWED_ORIGIN"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Print first few characters of API keys for verification
            if 'API_KEY' in var:
                print(f"✓ {var} found: {value[:8]}...")
            else:
                print(f"✓ {var} found: {value}")
    
    if missing_vars:
        print("WARNING: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        return False
    
    print("✓ All required environment variables are set")
    return True

def main():
    """Run all tests"""
    print("Starting deployment tests...")
    
    # Load environment variables first
    load_env_file()
    
    # Run all tests
    env_test = test_environment()
    vars_test = verify_environment_variables()
    install_test = test_installation()
    if install_test:
        startup_test = test_application_startup()
    else:
        startup_test = False
    
    # Print summary
    print_section("Test Summary")
    print(f"Environment Check: {'✓' if env_test else '✗'}")
    print(f"Environment Variables: {'✓' if vars_test else '✗'}")
    print(f"Installation: {'✓' if install_test else '✗'}")
    print(f"Application Startup: {'✓' if startup_test else '✗'}")
    
    if all([env_test, vars_test, install_test, startup_test]):
        print("\nAll tests passed! Ready for deployment.")
        return 0
    else:
        print("\nSome tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
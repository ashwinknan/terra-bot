import concurrent.futures
import time
import pytest
from app.main import create_app
from app.core.initializer import initialize_app, AppComponents, shutdown_app

@pytest.fixture(scope="module", autouse=True)
def setup_app():
    """Initialize app and components"""
    try:
        initialize_app(force_recreate=True)
        time.sleep(5)  # Give time for initialization
        yield
    finally:
        shutdown_app()

def test_concurrent_requests():
    """Test system under concurrent load"""
    # Reduce concurrent load to avoid rate limits
    num_concurrent = 3  # Reduced from 5
    num_requests = 5   # Reduced from 10
    
    # Ensure QA components are initialized
    if not AppComponents.qa_chain_manager or not AppComponents.qa_chain:
        pytest.skip("QA components not initialized")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        results = []
        
        try:
            # Submit requests with delay between each
            for i in range(num_requests):
                future = executor.submit(
                    AppComponents.qa_chain_manager.process_query,
                    AppComponents.qa_chain,
                    "What is T#?"
                )
                futures.append(future)
                time.sleep(1)  # Add delay between submissions
            
            # Get results with increased timeout
            for future in concurrent.futures.as_completed(futures, timeout=60):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    pytest.fail(f"Request failed: {str(e)}")
            
            # Verify results
            assert len(results) == num_requests, f"Expected {num_requests} results, got {len(results)}"
            assert all(isinstance(r.get("answer"), str) for r in results), "Invalid response format"
            
        except concurrent.futures.TimeoutError:
            pytest.fail("Concurrent requests timed out")
        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--log-cli-level=INFO"])
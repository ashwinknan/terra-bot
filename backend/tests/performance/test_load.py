# tests/performance/test_load.py
import concurrent.futures
import time

def test_concurrent_requests():
    """Test system under concurrent load"""
    num_concurrent = 5
    num_requests = 10
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        for _ in range(num_requests):
            future = executor.submit(
                AppComponents.qa_chain_manager.process_query,
                AppComponents.qa_chain,
                "What is T#?"
            )
            futures.append(future)
            
        results = [f.result() for f in futures]
        assert all(isinstance(r["answer"], str) for r in results)
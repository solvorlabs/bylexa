# test_sandbox.py
from bylexa.script_sandbox import run_code_in_sandbox

def test_sandbox():
    print("=== Testing Script Sandbox ===")
    
    # Test safe code
    safe_code = '''
import math
result = math.sqrt(16)
print(f"Square root of 16: {result}")
'''
    
    result = run_code_in_sandbox(safe_code, timeout=5)
    print(f"Safe code result: {result}")
    
    # Test restricted import
    restricted_code = '''
import os
print(os.listdir("."))
'''
    
    result = run_code_in_sandbox(restricted_code, timeout=5)
    print(f"Restricted code result: {result}")
    
    # Test timeout
    timeout_code = '''
import time
time.sleep(20)  # Should timeout
print("This should not print")
'''
    
    result = run_code_in_sandbox(timeout_code, timeout=2)
    print(f"Timeout test result: {result}")
    
    # Test memory limit (if supported)
    memory_code = '''
big_list = [0] * 1000000  # Large memory allocation
print("Memory test completed")
'''
    
    result = run_code_in_sandbox(memory_code, max_memory=50)  # 50MB limit
    print(f"Memory test result: {result}")

if __name__ == "__main__":
    test_sandbox()
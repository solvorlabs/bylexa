# test_orchestrator.py
from bylexa.ai_orchestrator import get_orchestrator
import time

def test_orchestrator():
    orchestrator = get_orchestrator()
    
    print("=== Testing Direct Commands ===")
    
    # Test clear command
    result = orchestrator.process_text("open notepad")
    print(f"Open Notepad: {result}")
    
    # Check execution result
    time.sleep(1)
    execution_result = orchestrator.get_execution_result()
    if execution_result:
        print(f"Execution Result: {execution_result}")
    
    print("\n=== Testing Ambiguous Commands ===")
    
    # Test ambiguous command
    result = orchestrator.process_text("play")
    print(f"Ambiguous Command: {result}")
    
    print("\n=== Testing Invalid Commands ===")
    
    # Test invalid command
    result = orchestrator.process_text("xyzabc invalid command")
    print(f"Invalid Command: {result}")

if __name__ == "__main__":
    test_orchestrator()
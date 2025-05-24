# run_all_tests.py
import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Run a single test file and return success status"""
    try:
        print(f"\n{'='*50}")
        print(f"Running: {test_file}")
        print('='*50)
        
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ PASSED")
            print(result.stdout)
            return True
        else:
            print("✗ FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ TIMEOUT")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    test_files = [
        "test_intent_parser.py",
        "test_dialog_manager.py", 
        "test_orchestrator.py",
        "test_plugins.py",
        "test_community_registry.py",
        "test_sandbox.py"
    ]
    
    passed = 0
    total = len(test_files)
    
    print("Starting Bylexa Component Tests...")
    
    for test_file in test_files:
        if Path(test_file).exists():
            if run_test(test_file):
                passed += 1
        else:
            print(f"⚠ Test file not found: {test_file}")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
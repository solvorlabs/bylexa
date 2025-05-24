# test_community_registry.py
from bylexa.community_registry import get_registry

def test_community_registry():
    registry = get_registry()
    
    print("=== Testing Community Registry ===")
    print(f"Local scripts directory: {registry.local_scripts_dir}")
    
    # Test script submission
    test_script = {
        "name": "test_calculator",
        "version": "1.0.0",
        "description": "A simple calculator script",
        "author": "Test User",
        "source": '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def run(operation, a, b):
    if operation == "add":
        return add(a, b)
    elif operation == "subtract":
        return subtract(a, b)
    else:
        return "Invalid operation"
''',
        "requirements": ["math"],
        "keywords": ["calculator", "math", "utility"]
    }
    
    # Submit script
    result = registry.submit_script(test_script)
    print(f"Script submission: {result}")
    
    # Search scripts
    search_results = registry.search_scripts("calculator", remote=False)
    print(f"Search results: {len(search_results)} scripts found")
    
    for script in search_results:
        print(f"  - {script['name']} v{script['version']}: {script['description']}")
    
    # Get specific script
    script = registry.get_script(name="test_calculator", remote=False)
    if script:
        print(f"Retrieved script: {script['name']}")
        print(f"Has source code: {'source' in script}")
    
    # Test module loading
    module = registry.load_script_module("test_calculator")
    if module:
        print("Module loaded successfully!")
        if hasattr(module, 'run'):
            result = module.run("add", 5, 3)
            print(f"Test calculation (5+3): {result}")

if __name__ == "__main__":
    test_community_registry()
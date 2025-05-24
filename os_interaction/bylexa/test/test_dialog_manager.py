# test_dialog_manager.py
from bylexa.dialog_manager import DialogManager
from bylexa.intent_parser import IntentParser

def test_dialog_flow():
    parser = IntentParser()
    dialog = DialogManager()
    
    # Test ambiguous resolution flow
    print("=== Testing Ambiguous Command Resolution ===")
    
    # Step 1: Send ambiguous command
    result = parser.parse_command("play")
    dialog_result = dialog.handle_response("play", result)
    print(f"Initial: {dialog_result}")
    
    # Step 2: Resolve ambiguity
    if dialog_result.get("status") == "ambiguous":
        resolution = dialog.handle_response("1", {})  # Choose first option
        print(f"Resolution: {resolution}")
    
    # Test parameter collection
    print("\n=== Testing Parameter Collection ===")
    result = parser.parse_command("open")
    dialog_result = dialog.handle_response("open", result)
    print(f"Missing param request: {dialog_result}")
    
    # Provide missing parameter
    if dialog_result.get("status") == "missing_params":
        completion = dialog.handle_response("chrome", {})
        print(f"Parameter provided: {completion}")

if __name__ == "__main__":
    test_dialog_flow()
# test_intent_parser.py
from bylexa.intent_parser import IntentParser

def test_intent_parser():
    parser = IntentParser()
    
    # Test basic command parsing
    result = parser.parse_command("open chrome")
    print(f"Open Chrome: {result}")
    
    # Test ambiguous commands
    result = parser.parse_command("play music")
    print(f"Play Music: {result}")
    
    # Test file operations
    result = parser.parse_command("copy file.txt to backup/")
    print(f"File Copy: {result}")
    
    # Test missing parameters
    result = parser.parse_command("open")
    print(f"Missing Params: {result}")

if __name__ == "__main__":
    test_intent_parser()
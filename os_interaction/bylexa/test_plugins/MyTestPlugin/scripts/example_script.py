
def run(context, **kwargs):
    """
    Example script for MyTestPlugin.
    
    Args:
        context: Execution context with user input and system state
        **kwargs: Additional parameters
    
    Returns:
        Result message or data
    """
    user_input = context.get("user_input", "")
    
    # Process user input and extract relevant information
    if "hello" in user_input.lower():
        return f"MyTestPlugin script: Hello there!"
    elif "status" in user_input.lower():
        return f"MyTestPlugin script: All systems operational"
    else:
        return f"MyTestPlugin script: Processed input: {user_input}"

def get_required_permissions():
    """Return list of required permissions for this script."""
    return ["file_read", "network_access"]

def get_trigger_patterns():
    """Return patterns that should trigger this script."""
    return [
        r".*mytestplugin.*hello.*",
        r".*mytestplugin.*status.*"
    ]

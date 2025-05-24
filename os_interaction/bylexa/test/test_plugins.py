# test_plugins.py
from bylexa.plugin_dev_kit import PluginManager
from pathlib import Path

def test_plugin_manager():
    # Create test plugins directory
    plugins_dir = Path("test_plugins")
    plugins_dir.mkdir(exist_ok=True)
    
    manager = PluginManager(plugins_dir)
    
    print("=== Plugin Manager Status ===")
    print(f"Plugins Directory: {manager.plugins_dir}")
    print(f"Loaded Plugins: {len(manager.plugins)}")
    
    # List loaded plugins
    for plugin_id, plugin_info in manager.plugins.items():
        print(f"Plugin: {plugin_id}")
        print(f"  Enabled: {plugin_info.get('enabled', False)}")
        print(f"  Metadata: {plugin_info.get('metadata', {})}")
    
    # Test plugin commands
    commands = manager.get_plugin_commands()
    print(f"\nAvailable Plugin Commands: {list(commands.keys())}")

# Create a sample test plugin
def create_test_plugin():
    plugins_dir = Path("test_plugins/sample_plugin")
    plugins_dir.mkdir(parents=True, exist_ok=True)
    
    # Create plugin.json
    plugin_json = {
        "name": "Sample Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "author": "Test Author"
    }
    
    with open(plugins_dir / "plugin.json", "w") as f:
        import json
        json.dump(plugin_json, f, indent=2)
    
    # Create main.py
    plugin_code = '''
from bylexa.plugin_dev_kit import PluginBase, plugin_command

class Plugin(PluginBase):
    @plugin_command(
        description="Test command that says hello",
        parameters={"name": {"type": "str", "default": "World"}}
    )
    def say_hello(self, params):
        name = params.get("name", "World")
        return f"Hello, {name}!"
'''
    
    with open(plugins_dir / "main.py", "w") as f:
        f.write(plugin_code)
    
    print(f"Created test plugin at: {plugins_dir}")

if __name__ == "__main__":
    create_test_plugin()
    test_plugin_manager()

from bylexa.plugin_dev_kit import PluginBase, plugin_command

class Plugin(PluginBase):
    """
    MyTestPlugin plugin for Bylexa.
    """
    
    @plugin_command(
        description="Example command for MyTestPlugin",
        parameters={
            "message": {"type": "str", "default": "Hello World"}
        }
    )
    def say_hello(self, params):
        """Say hello with a custom message."""
        message = params.get("message", "Hello World")
        return f"MyTestPlugin says: {message}"
    
    @plugin_command(
        description="Get plugin status",
        parameters={}
    )
    def get_status(self, params):
        """Get the current status of the plugin."""
        return {
            "status": "active",
            "plugin": "MyTestPlugin",
            "version": self.metadata.get("version", "unknown")
        }

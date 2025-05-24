
from bylexa.plugin_dev_kit import PluginBase, plugin_command

class Plugin(PluginBase):
    @plugin_command(
        description="Test command that says hello",
        parameters={"name": {"type": "str", "default": "World"}}
    )
    def say_hello(self, params):
        name = params.get("name", "World")
        return f"Hello, {name}!"

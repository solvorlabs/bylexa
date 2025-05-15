import inspect
import logging
import json
import os
import sys
import functools
from typing import Dict, List, Any, Optional, Callable, Union, Type
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PluginBase:
    """
    Base class for all Bylexa plugins.
    Provides utility methods and standardized interfaces.
    """
    
    def __init__(self, plugin_id: str, metadata: Dict = None):
        """
        Initialize the plugin base.
        
        Args:
            plugin_id: Unique identifier for the plugin
            metadata: Plugin metadata dictionary
        """
        self.plugin_id = plugin_id
        self.metadata = metadata or {}
        self.commands = {}
        self.hooks = {}
        
        # Register decorated commands and hooks
        self._register_decorated_methods()
    
    def _register_decorated_methods(self):
        """Register methods decorated with @plugin_command or @plugin_hook."""
        for name, method in inspect.getmembers(self, inspect.ismethod):
            # Check for command metadata
            if hasattr(method, '_command_info'):
                self.commands[name] = method._command_info
                logger.debug(f"Registered plugin command: {name}")
            
            # Check for hook metadata
            if hasattr(method, '_hook_info'):
                hook_type = method._hook_info.get('type')
                if hook_type:
                    if hook_type not in self.hooks:
                        self.hooks[hook_type] = []
                    self.hooks[hook_type].append(method)
                    logger.debug(f"Registered plugin hook: {hook_type} -> {name}")
    
    def handle_action(self, action: str, command: Dict) -> Optional[str]:
        """
        Handle a command action if supported by this plugin.
        
        Args:
            action: The action name
            command: The command dictionary
            
        Returns:
            Result string if handled, None otherwise
        """
        # Check if this is a direct plugin command
        if action.startswith(f"{self.plugin_id}."):
            # Extract the specific command name
            cmd_name = action[len(f"{self.plugin_id}."): ] 
            if cmd_name in self.commands:
                logger.info(f"Plugin {self.plugin_id} handling command: {cmd_name}")
                try:
                    # Get the method for this command
                    method = getattr(self, cmd_name)
                    
                    # Extract parameters for the command
                    params = {}
                    cmd_info = self.commands[cmd_name]
                    if 'parameters' in cmd_info:
                        for param_name, param_info in cmd_info['parameters'].items():
                            if param_name in command:
                                params[param_name] = command[param_name]
                    
                    # Call the method with parameters
                    result = method(params)
                    return str(result)
                
                except Exception as e:
                    logger.error(f"Error executing plugin command {cmd_name}: {str(e)}")
                    return f"Error in plugin {self.plugin_id}: {str(e)}"
        
        # Not handled by this plugin
        return None
    
    def get_commands(self) -> Dict[str, Dict]:
        """
        Get all commands provided by this plugin.
        
        Returns:
            Dictionary mapping command names to their metadata
        """
        return self.commands
    
    def get_hooks(self, hook_type: str = None) -> Dict[str, List[Callable]]:
        """
        Get hooks provided by this plugin.
        
        Args:
            hook_type: Optional filter for specific hook type
            
        Returns:
            Dictionary mapping hook types to lists of handler methods
        """
        if hook_type:
            return {hook_type: self.hooks.get(hook_type, [])}
        return self.hooks
    
    def on_load(self) -> bool:
        """
        Called when the plugin is loaded.
        Override this method to perform initialization.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        return True
    
    def on_unload(self) -> bool:
        """
        Called when the plugin is unloaded.
        Override this method to perform cleanup.
        
        Returns:
            True if unloaded successfully, False otherwise
        """
        return True


def plugin_command(description: str = "", parameters: Dict = None):
    """
    Decorator for plugin command methods.
    
    Args:
        description: Command description
        parameters: Dictionary mapping parameter names to their specifications
        
    Returns:
        Decorated method
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, params=None):
            if params is None:
                params = {}
            return func(self, params)
        
        # Store command metadata in the method object
        wrapper._command_info = {
            'description': description,
            'parameters': parameters or {}
        }
        
        return wrapper
    
    return decorator


def plugin_hook(hook_type: str, priority: int = 100):
    """
    Decorator for plugin hook methods.
    
    Args:
        hook_type: Type of hook (e.g., 'before_command', 'after_command')
        priority: Hook priority (lower numbers run first)
        
    Returns:
        Decorated method
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Store hook metadata in the method object
        wrapper._hook_info = {
            'type': hook_type,
            'priority': priority
        }
        
        return wrapper
    
    return decorator


class PluginManager:
    """
    Manager for loading, unloading, and interacting with plugins.
    """
    
    def __init__(self, plugins_dir: Path):
        """
        Initialize the plugin manager.
        
        Args:
            plugins_dir: Path to the plugins directory
        """
        self.plugins_dir = plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Dictionary to store loaded plugins
        self.plugins = {}
        
        # Load plugins configuration
        self.config_file = self.plugins_dir / 'plugins.json'
        self._load_config()
    
    def _load_config(self):
        """Load plugins configuration from file."""
        if not self.config_file.exists():
            # Create default config if it doesn't exist
            self.config = {"plugins": {}}
            self._save_config()
        else:
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                logger.error("Invalid plugins configuration file")
                self.config = {"plugins": {}}
                self._save_config()
    
    def _save_config(self):
        """Save plugins configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_all_plugins(self):
        """Load all plugins in the plugins directory."""
        # Ensure the plugins directory exists
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # Find plugin directories
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            
            plugin_id = plugin_dir.name
            
            # Skip already loaded plugins
            if plugin_id in self.plugins:
                continue
            
            # Check if plugin is in config
            if plugin_id not in self.config.get('plugins', {}):
                self.config.setdefault('plugins', {})[plugin_id] = {
                    "enabled": True,
                    "metadata": {}
                }
                self._save_config()
            
            # Load the plugin if enabled
            if self.config['plugins'][plugin_id].get('enabled', True):
                self.load_plugin(plugin_id)
            else:
                logger.info(f"Plugin {plugin_id} is disabled, skipping")
    
    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load a specific plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to load
            
        Returns:
            True if plugin was loaded successfully, False otherwise
        """
        plugin_dir = self.plugins_dir / plugin_id
        
        if not plugin_dir.exists() or not plugin_dir.is_dir():
            logger.error(f"Plugin directory not found: {plugin_dir}")
            return False
        
        # Check for main.py file
        main_file = plugin_dir / 'main.py'
        if not main_file.exists():
            logger.error(f"Plugin main.py not found: {main_file}")
            return False
        
        # Load metadata from plugin.json if available
        metadata = {}
        metadata_file = plugin_dir / 'plugin.json'
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid plugin metadata file: {metadata_file}")
        
        try:
            # Add plugin directory to sys.path temporarily
            if str(plugin_dir) not in sys.path:
                sys.path.insert(0, str(plugin_dir))
            
            # Import the plugin module
            module_name = f"bylexa_plugin_{plugin_id}"
            
            # Use importlib to load the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, main_file)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load plugin specification from {main_file}")
                return False
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Check if the module has a Plugin class that inherits from PluginBase
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and 
                    attr is not PluginBase and 
                    issubclass(attr, PluginBase)):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                logger.error(f"No Plugin class found in {main_file}")
                return False
            
            # Create plugin instance
            plugin_instance = plugin_class(plugin_id, metadata)
            
            # Call on_load method
            if not plugin_instance.on_load():
                logger.error(f"Plugin {plugin_id} on_load() returned False")
                return False
            
            # Store the plugin
            self.plugins[plugin_id] = {
                "id": plugin_id,
                "enabled": True,
                "metadata": metadata,
                "module": module,
                "instance": plugin_instance,
                "class": plugin_class
            }
            
            logger.info(f"Plugin {plugin_id} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {str(e)}")
            return False
        finally:
            # Remove from sys.path
            if str(plugin_dir) in sys.path:
                sys.path.remove(str(plugin_dir))
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a specific plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to unload
            
        Returns:
            True if plugin was unloaded successfully, False otherwise
        """
        if plugin_id not in self.plugins:
            logger.warning(f"Plugin {plugin_id} not loaded")
            return False
        
        try:
            # Call on_unload method
            plugin_instance = self.plugins[plugin_id]["instance"]
            plugin_instance.on_unload()
            
            # Remove from loaded plugins
            del self.plugins[plugin_id]
            
            # Remove module from sys.modules
            module_name = f"bylexa_plugin_{plugin_id}"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            logger.info(f"Plugin {plugin_id} unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {str(e)}")
            return False
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            plugin_id: ID of the plugin to enable
            
        Returns:
            True if successful, False otherwise
        """
        if plugin_id not in self.config.get('plugins', {}):
            self.config.setdefault('plugins', {})[plugin_id] = {"enabled": True}
        else:
            self.config['plugins'][plugin_id]["enabled"] = True
        
        self._save_config()
        
        # Load the plugin if it's not already loaded
        if plugin_id not in self.plugins:
            return self.load_plugin(plugin_id)
        
        return True
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            plugin_id: ID of the plugin to disable
            
        Returns:
            True if successful, False otherwise
        """
        if plugin_id not in self.config.get('plugins', {}):
            self.config.setdefault('plugins', {})[plugin_id] = {"enabled": False}
        else:
            self.config['plugins'][plugin_id]["enabled"] = False
        
        self._save_config()
        
        # Unload the plugin if it's loaded
        if plugin_id in self.plugins:
            return self.unload_plugin(plugin_id)
        
        return True
    
    def get_plugin_commands(self) -> Dict[str, Dict]:
        """
        Get all commands provided by loaded plugins.
        
        Returns:
            Dictionary mapping command names (including plugin prefix) to their metadata
        """
        commands = {}
        for plugin_id, plugin in self.plugins.items():
            if not plugin.get("enabled", False):
                continue
                
            instance = plugin.get("instance")
            if instance:
                plugin_commands = instance.get_commands()
                for cmd_name, cmd_info in plugin_commands.items():
                    # Add plugin prefix to command name
                    full_cmd_name = f"{plugin_id}.{cmd_name}"
                    commands[full_cmd_name] = cmd_info
        
        return commands
    
    def find_hook_handlers(self, hook_type: str) -> List[Callable]:
        """
        Find all handlers for a specific hook type across all plugins.
        
        Args:
            hook_type: Type of hook to find handlers for
            
        Returns:
            List of hook handler methods
        """
        handlers = []
        for plugin_id, plugin in self.plugins.items():
            if not plugin.get("enabled", False):
                continue
                
            instance = plugin.get("instance")
            if instance:
                plugin_hooks = instance.get_hooks(hook_type)
                if hook_type in plugin_hooks:
                    handlers.extend(plugin_hooks[hook_type])
        
        # Sort by priority (lower numbers first)
        handlers.sort(key=lambda h: getattr(h, '_hook_info', {}).get('priority', 100))
        return handlers
    
    def execute_hooks(self, hook_type: str, *args, **kwargs) -> List[Any]:
        """
        Execute all handlers for a specific hook type.
        
        Args:
            hook_type: Type of hook to execute
            *args, **kwargs: Arguments to pass to hook handlers
            
        Returns:
            List of results from all hook handlers
        """
        results = []
        handlers = self.find_hook_handlers(hook_type)
        
        for handler in handlers:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing hook handler: {str(e)}")
                results.append(None)
        
        return results
    
    def handle_action(self, action: str, command: Dict) -> Optional[str]:
        """
        Try to handle an action with all loaded plugins.
        
        Args:
            action: The action name
            command: The command dictionary
            
        Returns:
            Result string if handled by a plugin, None otherwise
        """
        for plugin_id, plugin in self.plugins.items():
            if not plugin.get("enabled", False):
                continue
                
            instance = plugin.get("instance")
            if instance:
                try:
                    result = instance.handle_action(action, command)
                    if result is not None:
                        return result
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_id}: {str(e)}")
        
        return None
    
    def get_available_plugins(self) -> List[Dict]:
        """
        Get a list of available plugins that could be installed.
        
        Returns:
            List of plugin metadata dictionaries
        """
        # In a real implementation, this would query a central plugin repository
        # For now, return a placeholder list
        return []
    
    def install_plugin(self, plugin_id: str) -> bool:
        """
        Install a plugin from a central repository.
        
        Args:
            plugin_id: ID of the plugin to install
            
        Returns:
            True if successful, False otherwise
        """
        # In a real implementation, this would download and install a plugin
        # For now, return a placeholder result
        logger.warning("Plugin installation not fully implemented")
        return False
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        Uninstall a plugin.
        
        Args:
            plugin_id: ID of the plugin to uninstall
            
        Returns:
            True if successful, False otherwise
        """
        # Unload the plugin first
        if plugin_id in self.plugins:
            self.unload_plugin(plugin_id)
        
        # Remove from config
        if plugin_id in self.config.get('plugins', {}):
            del self.config['plugins'][plugin_id]
            self._save_config()
        
        # Delete plugin directory
        plugin_dir = self.plugins_dir / plugin_id
        if plugin_dir.exists() and plugin_dir.is_dir():
            try:
                import shutil
                shutil.rmtree(plugin_dir)
                logger.info(f"Plugin {plugin_id} uninstalled successfully")
                return True
            except Exception as e:
                logger.error(f"Error removing plugin directory: {str(e)}")
        
        return False
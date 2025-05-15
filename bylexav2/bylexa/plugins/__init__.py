from typing import Dict, Any, List, Optional
from pathlib import Path
import importlib
import json
import os
import requests
import zipfile
import shutil

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.plugin_dir = Path.home() / '.bylexa' / 'plugins'
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugin_registry_url = "http://localhost:3000/api/plugins/registry"
        # self.plugin_registry_url = "https://bylexa.onrender.com/api/plugins/registry"
        self.load_plugins()

    def load_plugins(self) -> None:
        """Load all installed plugins"""
        for plugin_path in self.plugin_dir.glob('*/plugin.json'):
            try:
                with open(plugin_path) as f:
                    metadata = json.load(f)
                
                plugin_name = metadata['name']
                module_path = plugin_path.parent / 'main.py'
                
                if module_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        f"bylexa.plugins.{plugin_name}",
                        str(module_path)
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        self.plugins[plugin_name] = {
                            'metadata': metadata,
                            'module': module,
                            'enabled': metadata.get('enabled', True)
                        }
            except Exception as e:
                print(f"Error loading plugin {plugin_path}: {e}")

    def get_available_plugins(self) -> List[Dict[str, Any]]:
        """Fetch available plugins from registry"""
        try:
            response = requests.get(self.plugin_registry_url)
            data = response.json()
            return data.get('plugins', [])  # Return plugins list directly
        except Exception as e:
            return []

    def install_plugin(self, plugin_id: str) -> bool:
        """Install a plugin from the registry"""
        try:
            print(f"Starting installation for plugin: {plugin_id}")

            # Download plugin
            download_url = f"{self.plugin_registry_url}/{plugin_id}/download"
            print(f"Downloading plugin from: {download_url}")
            response = requests.get(download_url)
            if response.status_code != 200:
                print(f"Failed to download plugin {plugin_id}. Status code: {response.status_code}")
                return False
            print(f"Successfully downloaded plugin {plugin_id}")

            # Create temporary file
            plugin_zip = self.plugin_dir / f"{plugin_id}.zip"
            print(f"Saving plugin zip to: {plugin_zip}")
            with open(plugin_zip, 'wb') as f:
                f.write(response.content)

            # Extract plugin
            extract_path = self.plugin_dir / plugin_id
            print(f"Extracting plugin to: {extract_path}")
            with zipfile.ZipFile(plugin_zip) as zf:
                zf.extractall(extract_path)

            # Cleanup
            print(f"Removing temporary zip file: {plugin_zip}")
            plugin_zip.unlink()

            # Reload plugins
            print(f"Reloading plugins after installation of {plugin_id}")
            self.load_plugins()

            print(f"Plugin {plugin_id} installed successfully!")
            return True

        except Exception as e:
            print(f"Error installing plugin {plugin_id}: {e}")
            return False


    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        try:
            plugin_path = self.plugin_dir / plugin_id
            if plugin_path.exists():
                shutil.rmtree(plugin_path)
                if plugin_id in self.plugins:
                    del self.plugins[plugin_id]
                return True
            return False
        except Exception as e:
            print(f"Error uninstalling plugin {plugin_id}: {e}")
            return False

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        try:
            if plugin_id in self.plugins:
                plugin_path = self.plugin_dir / plugin_id / 'plugin.json'
                with open(plugin_path) as f:
                    metadata = json.load(f)
                metadata['enabled'] = True
                with open(plugin_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                self.plugins[plugin_id]['enabled'] = True
                return True
            return False
        except Exception as e:
            print(f"Error enabling plugin {plugin_id}: {e}")
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        try:
            if plugin_id in self.plugins:
                plugin_path = self.plugin_dir / plugin_id / 'plugin.json'
                with open(plugin_path) as f:
                    metadata = json.load(f)
                metadata['enabled'] = False
                with open(plugin_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                self.plugins[plugin_id]['enabled'] = False
                return True
            return False
        except Exception as e:
            print(f"Error disabling plugin {plugin_id}: {e}")
            return False

# Singleton instance
plugin_manager = PluginManager()
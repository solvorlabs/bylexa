import logging
import json
import os
import re
import sys
import uuid
import hashlib
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import requests
from datetime import datetime
import shutil
import importlib.util

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommunityRegistry:
    """
    Service for submitting, retrieving, and managing community scripts/plugins.
    Provides both local and remote registry functionality.
    """
    
    def __init__(self, registry_url: str = None, local_scripts_dir: Path = None):
        """
        Initialize the community registry.
        
        Args:
            registry_url: URL of the remote script registry API
            local_scripts_dir: Path to local scripts directory
        """
        # Set default registry URL for remote operations
        self.registry_url = registry_url or "http://localhost:3000/api/scripts/registry"
        
        # Set up local scripts directory
        if local_scripts_dir:
            self.local_scripts_dir = local_scripts_dir
        else:
            # Default to ~/.bylexa/community_scripts
            self.local_scripts_dir = Path.home() / '.bylexa' / 'community_scripts'
        
        # Create directory if it doesn't exist
        self.local_scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize local registry file
        self.local_registry_file = self.local_scripts_dir / 'registry.json'
        if not self.local_registry_file.exists():
            with open(self.local_registry_file, 'w') as f:
                json.dump({"scripts": []}, f)
        
        # Load local registry
        self._load_local_registry()
    
    def _load_local_registry(self):
        """Load the local registry file."""
        try:
            with open(self.local_registry_file, 'r') as f:
                self.local_registry = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Local registry file not found or invalid, creating new one")
            self.local_registry = {"scripts": []}
            self._save_local_registry()
    
    def _save_local_registry(self):
        """Save the local registry to file."""
        with open(self.local_registry_file, 'w') as f:
            json.dump(self.local_registry, f, indent=2)
    
    def submit_script(self, script_data: Dict) -> Dict:
        """
        Submit a script to the community registry.
        
        Args:
            script_data: Dictionary containing script metadata and source
                Required fields: name, version, description, author, source, requirements
                
        Returns:
            Response dictionary with status and message
        """
        # Validate required fields
        required_fields = ['name', 'version', 'description', 'author', 'source']
        for field in required_fields:
            if field not in script_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        # Clean and validate script name
        script_data['name'] = re.sub(r'[^a-zA-Z0-9_]', '_', script_data['name'])
        if not script_data['name']:
            return {
                "status": "error",
                "message": "Invalid script name"
            }
        
        # Add timestamp and generate script ID if not provided
        script_data['submitted_at'] = datetime.now().isoformat()
        if 'script_id' not in script_data:
            script_data['script_id'] = str(uuid.uuid4())
        
        # Save script to local registry first
        try:
            # Create a clean copy of script data for local registry
            local_script_data = script_data.copy()
            
            # Add to local registry
            for i, script in enumerate(self.local_registry["scripts"]):
                if script.get('name') == local_script_data['name']:
                    # Update existing script
                    self.local_registry["scripts"][i] = local_script_data
                    break
            else:
                # Add new script
                self.local_registry["scripts"].append(local_script_data)
            
            # Save to local registry file
            self._save_local_registry()
            
            # Save script file
            script_file = self.local_scripts_dir / f"{local_script_data['name']}.py"
            with open(script_file, 'w') as f:
                f.write(local_script_data['source'])
            
            logger.info(f"Script {local_script_data['name']} saved to local registry")
            
            # Submit to remote registry if URL is available
            if self.registry_url:
                try:
                    response = requests.post(
                        self.registry_url,
                        json=script_data
                    )
                    
                    if response.status_code == 200 or response.status_code == 201:
                        logger.info(f"Script {script_data['name']} submitted to remote registry")
                        return {
                            "status": "success",
                            "message": f"Script submitted successfully: {script_data['name']}",
                            "script_id": script_data['script_id'],
                            "remote": True
                        }
                    else:
                        logger.warning(f"Remote submission failed: {response.status_code} - {response.text}")
                        return {
                            "status": "partial",
                            "message": f"Script saved locally but remote submission failed: {response.text}",
                            "script_id": script_data['script_id'],
                            "remote": False
                        }
                
                except requests.RequestException as e:
                    logger.error(f"Error submitting to remote registry: {str(e)}")
                    return {
                        "status": "partial",
                        "message": f"Script saved locally but remote submission failed: {str(e)}",
                        "script_id": script_data['script_id'],
                        "remote": False
                    }
            
            # If no remote URL or submission not attempted
            return {
                "status": "success",
                "message": f"Script saved to local registry: {script_data['name']}",
                "script_id": script_data['script_id'],
                "remote": False
            }
        
        except Exception as e:
            logger.error(f"Error saving script to local registry: {str(e)}")
            return {
                "status": "error",
                "message": f"Error saving script: {str(e)}"
            }
    
    def search_scripts(self, query: str = "", remote: bool = True) -> List[Dict]:
        """
        Search for scripts in the registry.
        
        Args:
            query: Search query string
            remote: Whether to search the remote registry (if available)
            
        Returns:
            List of matching script dictionaries
        """
        results = []
        
        # Search local registry first
        if query:
            query_lower = query.lower()
            for script in self.local_registry.get("scripts", []):
                # Check if query matches name, description, or keywords
                if (query_lower in script.get('name', '').lower() or
                    query_lower in script.get('description', '').lower() or
                    any(query_lower in kw.lower() for kw in script.get('keywords', []))):
                    results.append(script)
        else:
            # No query, return all scripts
            results = self.local_registry.get("scripts", [])
        
        # Add source from local file if available
        for script in results:
            script_file = self.local_scripts_dir / f"{script['name']}.py"
            if script_file.exists():
                with open(script_file, 'r') as f:
                    script['source'] = f.read()
        
        # Search remote registry if requested and available
        if remote and self.registry_url:
            try:
                params = {'q': query} if query else {}
                response = requests.get(self.registry_url, params=params)
                
                if response.status_code == 200:
                    remote_scripts = response.json().get('scripts', [])
                    
                    # Filter out scripts already in local results (by ID or name)
                    local_ids = {s.get('script_id') for s in results if 'script_id' in s}
                    local_names = {s.get('name') for s in results if 'name' in s}
                    
                    for script in remote_scripts:
                        if (script.get('script_id') not in local_ids and
                            script.get('name') not in local_names):
                            script['remote_only'] = True
                            results.append(script)
                
                else:
                    logger.warning(f"Remote search failed: {response.status_code} - {response.text}")
            
            except requests.RequestException as e:
                logger.error(f"Error searching remote registry: {str(e)}")
        
        return results
    
    def get_script(self, script_id: str = None, name: str = None, remote: bool = True) -> Optional[Dict]:
        """
        Get a specific script by ID or name.
        
        Args:
            script_id: ID of the script to retrieve
            name: Name of the script to retrieve (used if ID not provided)
            remote: Whether to check the remote registry if not found locally
            
        Returns:
            Script dictionary or None if not found
        """
        # Check local registry first
        if script_id:
            for script in self.local_registry.get("scripts", []):
                if script.get('script_id') == script_id:
                    # Add source from local file if available
                    script_file = self.local_scripts_dir / f"{script['name']}.py"
                    if script_file.exists():
                        with open(script_file, 'r') as f:
                            script['source'] = f.read()
                    return script
        
        elif name:
            for script in self.local_registry.get("scripts", []):
                if script.get('name') == name:
                    # Add source from local file if available
                    script_file = self.local_scripts_dir / f"{script['name']}.py"
                    if script_file.exists():
                        with open(script_file, 'r') as f:
                            script['source'] = f.read()
                    return script
        
        # Not found locally, check remote if requested
        if remote and self.registry_url:
            try:
                url = f"{self.registry_url}/{script_id}" if script_id else f"{self.registry_url}/name/{name}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Remote script retrieval failed: {response.status_code} - {response.text}")
            
            except requests.RequestException as e:
                logger.error(f"Error retrieving script from remote registry: {str(e)}")
        
        return None
    
    def download_script(self, script_id: str = None, name: str = None) -> Dict:
        """
        Download a script from the remote registry and save it locally.
        
        Args:
            script_id: ID of the script to download
            name: Name of the script to download (used if ID not provided)
            
        Returns:
            Response dictionary with status and message
        """
        if not script_id and not name:
            return {
                "status": "error",
                "message": "Either script_id or name must be provided"
            }
        
        if not self.registry_url:
            return {
                "status": "error",
                "message": "Remote registry URL not available"
            }
        
        # Try to get script from remote registry
        try:
            url = f"{self.registry_url}/{script_id}/download" if script_id else f"{self.registry_url}/name/{name}/download"
            response = requests.get(url)
            
            if response.status_code == 200:
                script_data = response.json()
                
                # Add to local registry
                self.submit_script(script_data)
                
                return {
                    "status": "success",
                    "message": f"Script {script_data.get('name')} downloaded and installed",
                    "script_data": script_data
                }
            else:
                return {
                    "status": "error",
                    "message": f"Remote download failed: {response.status_code} - {response.text}"
                }
        
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Error downloading script: {str(e)}"
            }
    
    def delete_script(self, script_id: str = None, name: str = None) -> Dict:
        """
        Delete a script from the local registry.
        
        Args:
            script_id: ID of the script to delete
            name: Name of the script to delete (used if ID not provided)
            
        Returns:
            Response dictionary with status and message
        """
        if not script_id and not name:
            return {
                "status": "error",
                "message": "Either script_id or name must be provided"
            }
        
        deleted = False
        script_name = None
        
        # Find and remove from local registry
        for i, script in enumerate(self.local_registry.get("scripts", [])):
            if (script_id and script.get('script_id') == script_id) or (name and script.get('name') == name):
                script_name = script.get('name')
                del self.local_registry["scripts"][i]
                deleted = True
                break
        
        if deleted and script_name:
            # Save updated registry
            self._save_local_registry()
            
            # Delete script file
            script_file = self.local_scripts_dir / f"{script_name}.py"
            if script_file.exists():
                script_file.unlink()
                
            return {
                "status": "success",
                "message": f"Script {script_name} deleted from local registry"
            }
        else:
            return {
                "status": "error",
                "message": "Script not found in local registry"
            }
    
    def load_script_module(self, name: str) -> Optional[Any]:
        """
        Load a script as a Python module.
        
        Args:
            name: Name of the script to load
            
        Returns:
            Loaded module or None if not found
        """
        script_file = self.local_scripts_dir / f"{name}.py"
        if not script_file.exists():
            logger.error(f"Script file not found: {script_file}")
            return None
        
        try:
            # Load module using importlib
            spec = importlib.util.spec_from_file_location(name, script_file)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load script specification from {script_file}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            logger.info(f"Loaded script module: {name}")
            return module
        
        except Exception as e:
            logger.error(f"Error loading script module {name}: {str(e)}")
            if name in sys.modules:
                del sys.modules[name]
            return None


# Singleton instance
_registry_instance = None

def get_registry() -> CommunityRegistry:
    """Get the global community registry instance."""
    global _registry_instance
    if _registry_instance is None:
        from .config import load_app_configs
        
        registry_url = load_app_configs().get('script_registry_url', "http://localhost:3000/api/scripts/registry")
        scripts_dir = Path(load_app_configs().get('community_scripts_directory', 'community_scripts'))
        
        # Convert relative path to absolute
        if not scripts_dir.is_absolute():
            scripts_dir = Path.home() / '.bylexa' / scripts_dir
        
        _registry_instance = CommunityRegistry(registry_url, scripts_dir)
    
    return _registry_instance
import os
import sys
import pickle
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
import tempfile
from pathlib import Path

class ScriptManager:
    """
    Manages script execution and WebDriver session handling for automation scripts.
    """
    
    def __init__(self, scripts_directory: str):
        self.scripts_directory = Path(scripts_directory)
        self.session_file = self.scripts_directory / 'webdriver_session.pkl'
        self._driver = None

    def get_driver(self) -> Optional[WebDriver]:
        """
        Gets an existing WebDriver instance or loads it from the session file.
        """
        if self._driver is not None:
            try:
                # Verify the session is still valid
                self._driver.current_url
                return self._driver
            except:
                self._driver = None

        # Try to load from session file
        if self.session_file.exists():
            try:
                with open(self.session_file, 'rb') as f:
                    session = pickle.load(f)
                
                driver = webdriver.Remote(
                    command_executor=session['command_executor_url'],
                    options=webdriver.ChromeOptions()
                )
                driver.session_id = session['session_id']
                
                # Verify the loaded session
                try:
                    driver.current_url
                    self._driver = driver
                    return driver
                except:
                    self.cleanup_session()
            except Exception as e:
                print(f"Error loading driver session: {str(e)}", file=sys.stderr)
        
        return None

    def save_driver_session(self, driver: WebDriver) -> None:
        """
        Saves the WebDriver session information.
        """
        try:
            session = {
                'command_executor_url': driver.command_executor._url,
                'session_id': driver.session_id
            }
            
            with open(self.session_file, 'wb') as f:
                pickle.dump(session, f)
            
            self._driver = driver
        except Exception as e:
            print(f"Error saving driver session: {str(e)}", file=sys.stderr)

    def cleanup_session(self) -> None:
        """
        Cleans up the session file and reference.
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            self._driver = None
        except Exception as e:
            print(f"Error cleaning up session: {str(e)}", file=sys.stderr)

    def perform_script(self, script_path: str, args: list, parameters: Dict[str, Any]) -> str:
        """
        Executes a script with WebDriver session handling.
        """
        try:
            # Import the script as a module
            sys.path.insert(0, str(self.scripts_directory))
            script_name = Path(script_path).stem
            script_module = __import__(script_name)
            
            # Get or create driver instance
            driver = self.get_driver()
            if driver is None:
                return "Error: No valid WebDriver session found"
            
            # Add the driver to the parameters
            parameters['driver'] = driver
            
            # Execute the main function if it exists
            if hasattr(script_module, 'main'):
                result = script_module.main(parameters)
            else:
                result = "Error: Script does not have a main function"
            
            return result
            
        except Exception as e:
            return f"Error executing script: {str(e)}"
        finally:
            sys.path.pop(0)

# Singleton instance
script_manager = None

def init_script_manager(scripts_directory: str) -> ScriptManager:
    """
    Initializes the script manager singleton.
    """
    global script_manager
    if script_manager is None:
        script_manager = ScriptManager(scripts_directory)
    return script_manager

def get_script_manager() -> ScriptManager:
    """
    Gets the script manager instance.
    """
    if script_manager is None:
        raise RuntimeError("Script manager not initialized")
    return script_manager
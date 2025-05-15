import os
import sys
import io
import threading
import traceback
import contextlib
import logging
import time
import json
import importlib
import builtins
import subprocess
from typing import Dict, Any, Optional, List, Callable, Set
from pathlib import Path
import multiprocessing
from multiprocessing import Process, Queue
import signal

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RestrictedEnvironment:
    """Context manager for a restricted execution environment."""
    
    def __init__(self, allowed_modules: List[str] = None, allowed_builtins: List[str] = None):
        """
        Initialize the restricted environment.
        
        Args:
            allowed_modules: List of module names that can be imported
            allowed_builtins: List of builtin functions that can be used
        """
        self.allowed_modules = set(allowed_modules or [])
        
        # Always allow these safe modules
        self.allowed_modules.update([
            'builtins', 'math', 'datetime', 'json', 're', 'string',
            'collections', 'random', 'itertools', 'functools',
            'pathlib', 'uuid', 'base64', 'hashlib', 'tempfile'
        ])
        
        self.allowed_builtins = set(allowed_builtins or [])
        
        # Always allow these safe builtins
        self.allowed_builtins.update([
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytes', 'chr',
            'complex', 'dict', 'dir', 'divmod', 'enumerate', 'filter',
            'float', 'format', 'frozenset', 'hash', 'hex', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min', 'next',
            'object', 'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed',
            'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type',
            'zip'
        ])
        
        # Save original import and builtins
        self.original_import = builtins.__import__
        self.original_builtins = dict(builtins.__dict__)
    
    def __enter__(self):
        """Enter the restricted environment."""
        # Replace __import__ with restricted version
        builtins.__import__ = self._restricted_import
        
        # Filter builtins
        for name in list(builtins.__dict__.keys()):
            if name not in self.allowed_builtins and not name.startswith('__'):
                delattr(builtins, name)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the restricted environment and restore original state."""
        # Restore original import
        builtins.__import__ = self.original_import
        
        # Restore original builtins
        for name in list(builtins.__dict__.keys()):
            if name not in self.original_builtins:
                delattr(builtins, name)
        
        for name, value in self.original_builtins.items():
            setattr(builtins, name, value)
    
    def _restricted_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Restricted version of __import__ that only allows approved modules."""
        if name not in self.allowed_modules:
            raise ImportError(f"Import of module '{name}' is not allowed in the restricted environment")
        
        return self.original_import(name, globals, locals, fromlist, level)


class ScriptSandbox:
    """
    Sandbox for safely executing untrusted Python code.
    Provides isolation and resource limitations.
    """
    
    def __init__(self, 
                 timeout: int = 10, 
                 max_memory: int = 100, 
                 allowed_modules: List[str] = None,
                 allowed_builtins: List[str] = None):
        """
        Initialize the script sandbox.
        
        Args:
            timeout: Maximum execution time in seconds
            max_memory: Maximum memory usage in MB
            allowed_modules: List of allowed modules to import
            allowed_builtins: List of allowed builtin functions
        """
        self.timeout = timeout
        self.max_memory = max_memory
        self.allowed_modules = allowed_modules or []
        self.allowed_builtins = allowed_builtins or []
    
    def run_untrusted_code(self, code: str, globals_dict: Dict = None) -> Dict[str, Any]:
        """
        Run untrusted code in a sandbox with resource limitations.
        
        Args:
            code: Python code string to execute
            globals_dict: Dictionary of global variables to provide
            
        Returns:
            Dictionary with execution results, output, and errors
        """
        # Create queues for result communication
        result_queue = Queue()
        
        # Create and start the isolated process
        process = Process(
            target=self._execute_in_process,
            args=(code, globals_dict, result_queue)
        )
        
        process.start()
        start_time = time.time()
        
        # Wait for the process with timeout
        process.join(self.timeout)
        
        # Check if the process is still running (timeout occurred)
        if process.is_alive():
            process.terminate()
            process.join(1)  # Give it a second to terminate
            
            # If still alive, force kill
            if process.is_alive():
                os.kill(process.pid, signal.SIGKILL)
            
            return {
                'success': False,
                'output': '',
                'errors': f'Execution timed out after {self.timeout} seconds',
                'exception': {
                    'type': 'TimeoutError',
                    'message': f'Code execution exceeded the {self.timeout} second limit',
                    'traceback': ''
                }
            }
        
        # Get the result if available
        try:
            result = result_queue.get(block=False)
            return result
        except Exception:
            return {
                'success': False,
                'output': '',
                'errors': 'Failed to retrieve execution result',
                'exception': {
                    'type': 'SandboxError',
                    'message': 'Failed to retrieve execution result',
                    'traceback': traceback.format_exc()
                }
            }
    
    def _execute_in_process(self, code: str, globals_dict: Dict, result_queue: Queue):
        """
        Execute code in a separate process with restricted environment.
        
        Args:
            code: Python code to execute
            globals_dict: Dictionary of global variables
            result_queue: Queue to communicate results back to parent
        """
        # Set resource limits for this process
        try:
            import resource
            
            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))
            
            # Set memory limit
            memory_bytes = self.max_memory * 1024 * 1024  # Convert MB to bytes
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        
        except ImportError:
            # resource module not available on Windows
            pass
        
        # Prepare result dictionary
        result = {
            'success': False,
            'output': '',
            'errors': '',
            'exception': None
        }
        
        # Create string buffers to capture output
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        # Create a restricted globals dictionary
        if globals_dict is None:
            globals_dict = {}
        
        # Set up a restricted locals dictionary
        locals_dict = {}
        
        try:
            # Enter restricted environment
            with RestrictedEnvironment(self.allowed_modules, self.allowed_builtins):
                # Redirect stdout and stderr
                with contextlib.redirect_stdout(output_buffer):
                    with contextlib.redirect_stderr(error_buffer):
                        # Compile and execute the code
                        compiled_code = compile(code, '<sandbox>', 'exec')
                        exec(compiled_code, globals_dict, locals_dict)
            
            # Set success flag
            result['success'] = True
            
        except Exception as e:
            # Capture exception details
            result['exception'] = {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
        
        finally:
            # Get output from buffers
            result['output'] = output_buffer.getvalue()
            result['errors'] = error_buffer.getvalue()
            
            # Close buffers
            output_buffer.close()
            error_buffer.close()
            
            # Put result in queue
            result_queue.put(result)


def run_code_in_sandbox(
    code: str, 
    globals_dict: Dict = None,
    timeout: int = 10,
    max_memory: int = 100,
    allowed_modules: List[str] = None,
    allowed_builtins: List[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run code in a sandbox.
    
    Args:
        code: Python code string to execute
        globals_dict: Dictionary of global variables
        timeout: Maximum execution time in seconds
        max_memory: Maximum memory usage in MB
        allowed_modules: List of allowed modules
        allowed_builtins: List of allowed builtin functions
        
    Returns:
        Dictionary with execution results
    """
    sandbox = ScriptSandbox(
        timeout=timeout,
        max_memory=max_memory,
        allowed_modules=allowed_modules,
        allowed_builtins=allowed_builtins
    )
    
    return sandbox.run_untrusted_code(code, globals_dict)


def validate_script(
    script_path: str,
    allowed_modules: List[str] = None,
    timeout: int = 5
) -> Dict[str, Any]:
    """
    Validate a script file by running it in a sandbox.
    
    Args:
        script_path: Path to the script file
        allowed_modules: List of allowed modules
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary with validation results
    """
    try:
        # Read the script file
        with open(script_path, 'r') as f:
            script_code = f.read()
        
        # Run in sandbox with minimal validation code
        validation_code = f"""
# Validation prelude
import ast
import inspect

# Parse the script to check for syntax errors
ast.parse('''{script_code}''')

# Execute the original script
{script_code}

# Additional validation checks
if 'run' in globals() and callable(globals()['run']):
    print("VALIDATION: Script has a valid 'run' function")
elif 'create_instance' in globals() and callable(globals()['create_instance']):
    print("VALIDATION: Script has a valid 'create_instance' function")
else:
    print("VALIDATION WARNING: Script does not have standard entry points")
"""
        
        # Run validation code in sandbox
        return run_code_in_sandbox(
            validation_code,
            timeout=timeout,
            allowed_modules=allowed_modules
        )
    
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'errors': f'Error during script validation: {str(e)}',
            'exception': {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
        }
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import json
import time
import asyncio
from pathlib import Path
import threading
import queue

from .intent_parser import IntentParser
from .dialog_manager import DialogManager
from .commands import perform_action

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Core orchestration layer for Bylexa's AI system.
    Manages the flow from voice/text input to command execution,
    handling ambiguity and parameter collection through dialog.
    """
    
    def __init__(self):
        """Initialize the AI orchestrator with necessary components."""
        self.parser = IntentParser()
        self.dialog_manager = DialogManager()
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self._executing = False
        self._execution_thread = None
        
        # Start the execution thread
        self._start_execution_thread()
    
    def _start_execution_thread(self):
        """Start a separate thread for command execution."""
        if self._execution_thread is None or not self._execution_thread.is_alive():
            self._executing = True
            self._execution_thread = threading.Thread(
                target=self._execution_loop, 
                daemon=True
            )
            self._execution_thread.start()
            logger.info("Command execution thread started")
    
    def _execution_loop(self):
        """Background loop to execute commands from the queue."""
        while self._executing:
            try:
                # Get a command from the queue with a timeout
                command = self.command_queue.get(timeout=0.5)
                
                # Execute the command
                logger.info(f"Executing command: {command}")
                result = perform_action(command)
                
                # Put the result in the response queue
                self.response_queue.put(result)
                
                # Mark task as done
                self.command_queue.task_done()
                
            except queue.Empty:
                # No commands in the queue, continue waiting
                pass
            except Exception as e:
                logger.error(f"Error in command execution: {str(e)}")
                # Put error in response queue
                self.response_queue.put(f"Error executing command: {str(e)}")
                # Mark task as done if there was a command
                if not self.command_queue.empty():
                    self.command_queue.task_done()
    
    def stop(self):
        """Stop the execution thread."""
        self._executing = False
        if self._execution_thread and self._execution_thread.is_alive():
            self._execution_thread.join(timeout=5.0)
            logger.info("Command execution thread stopped")
    
    def process_text(self, text: str) -> Dict:
        """
        Process text input and determine the appropriate action.
        
        Args:
            text: The text input to process
            
        Returns:
            Dictionary with response information
        """
        # Step 1: Parse the text to identify intent and extract parameters
        parser_result = self.parser.parse_command(text)
        logger.info(f"Parser result: {parser_result}")
        
        # Step 2: Use dialog manager to handle the parser result
        dialog_result = self.dialog_manager.handle_response(text, parser_result)
        logger.info(f"Dialog result: {dialog_result}")
        
        # Step 3: Execute command if dialog indicates we should
        if dialog_result.get("should_execute", False) and "command" in dialog_result:
            # Add command to execution queue
            self.command_queue.put(dialog_result["command"])
            
            # Return response with execution status
            return {
                "status": "executing",
                "message": dialog_result.get("message", "Executing command..."),
                "command": dialog_result["command"]
            }
        
        # Return dialog response if not executing
        return {
            "status": dialog_result.get("status", "unknown"),
            "message": dialog_result.get("message", "Unknown command"),
            "command": dialog_result.get("command", None)
        }
    
    def execute_voice_command(self, text: str) -> Dict:
        """
        Process and execute a voice command.
        
        Args:
            text: The transcribed voice command text
            
        Returns:
            Dictionary with response information
        """
        # For now, voice commands go through the same flow as text
        return self.process_text(text)
    
    def get_execution_result(self, timeout: float = 0.1) -> Optional[str]:
        """
        Check if there are any execution results available.
        
        Args:
            timeout: How long to wait for a result (seconds)
            
        Returns:
            The result string if available, None otherwise
        """
        try:
            return self.response_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def has_pending_commands(self) -> bool:
        """Check if there are any commands pending execution."""
        return not self.command_queue.empty()
    
    def clear_queues(self):
        """Clear both command and response queues."""
        # Clear command queue
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
                self.command_queue.task_done()
            except queue.Empty:
                break
        
        # Clear response queue
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.info("Command and response queues cleared")


# Singleton instance
_orchestrator_instance = None

def get_orchestrator() -> AIOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AIOrchestrator()
    return _orchestrator_instance

def init_orchestrator() -> AIOrchestrator:
    """Initialize and get the global orchestrator instance."""
    return get_orchestrator()
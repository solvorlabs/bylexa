import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import re

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DialogContext:
    """
    Class to manage and track conversation context.
    """
    def __init__(self):
        """Initialize the dialog context."""
        self.state = "initial"
        self.command = None
        self.missing_params = []
        self.options = []
        self.history = []
        self.last_response = None
        self.original_text = None
    
    def update(self, **kwargs):
        """Update context with new values."""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def add_to_history(self, user_input: str, system_response: str):
        """Add an exchange to the conversation history."""
        self.history.append({
            "user": user_input,
            "system": system_response
        })
        self.last_response = system_response
    
    def reset(self):
        """Reset the context to initial state."""
        self.state = "initial"
        self.command = None
        self.missing_params = []
        self.options = []
        self.last_response = None
        self.original_text = None
        # Keep history

class DialogManager:
    """
    Manages dialog with users to handle ambiguous commands
    and collect missing parameters.
    """
    def __init__(self):
        """Initialize the dialog manager."""
        self.context = DialogContext()
    
    def handle_response(self, user_input: str, parser_result: Dict) -> Dict:
        """
        Process user input based on current dialog state.
        
        Args:
            user_input: The user's input text
            parser_result: The result from IntentParser
            
        Returns:
            Dict with response and updated context
        """
        logger.info(f"Handling response in state: {self.context.state}")
        logger.info(f"Parser result: {parser_result}")
        
        # Update context with the original text if available
        if "original_text" in parser_result:
            self.context.original_text = parser_result["original_text"]
        
        # Handle based on the current state
        if self.context.state == "initial":
            return self._handle_initial_state(parser_result)
        elif self.context.state == "ambiguous":
            return self._resolve_ambiguity(user_input)
        elif self.context.state == "missing_params":
            return self._collect_parameters(user_input)
        else:
            # Unknown state, reset to initial
            self.context.reset()
            return {
                "status": "error",
                "message": "Dialog system error. Starting over.",
                "should_execute": False
            }
    
    def _handle_initial_state(self, parser_result: Dict) -> Dict:
        """Handle the initial state based on parser results."""
        status = parser_result.get("status")
        
        if status == "clear":
            # Command is ready to execute
            self.context.update(
                state="clear",
                command=parser_result["command"]
            )
            return {
                "status": "clear",
                "message": f"Executing command: {parser_result['command']['action']}",
                "command": parser_result["command"],
                "should_execute": True
            }
        
        elif status == "ambiguous":
            # Multiple possible commands, need clarification
            self.context.update(
                state="ambiguous",
                options=parser_result["options"]
            )
            
            # Generate clarification message
            option_texts = []
            for i, option in enumerate(parser_result["options"][:5]):  # Limit to top 5
                desc = option.get("description", option["action"])
                option_texts.append(f"{i+1}. {desc}")
            
            options_text = "\n".join(option_texts)
            message = (
                f"I'm not sure which command you want to run. "
                f"Please choose one of the following options by number or name:\n{options_text}"
            )
            
            return {
                "status": "ambiguous",
                "message": message,
                "should_execute": False
            }
        
        elif status == "missing_params":
            # Command is identified but missing parameters
            self.context.update(
                state="missing_params",
                command=parser_result["command"],
                missing_params=parser_result["missing_params"]
            )
            
            # Ask for the first missing parameter
            param = self.context.missing_params[0]
            message = f"Please provide the {param} for the {parser_result['command']['action']} command:"
            
            return {
                "status": "missing_params",
                "message": message,
                "should_execute": False
            }
        
        else:  # status == "error" or other
            # Error or unrecognized command
            message = parser_result.get("message", "I couldn't understand that command.")
            
            return {
                "status": "error",
                "message": message,
                "should_execute": False
            }
    
    def _resolve_ambiguity(self, user_input: str) -> Dict:
        """Resolve ambiguity by processing user's choice."""
        if not self.context.options:
            self.context.reset()
            return {
                "status": "error",
                "message": "No options available. Please state your command again.",
                "should_execute": False
            }
        
        selected_option = None
        
        # Check if user entered a number
        if user_input.isdigit():
            option_num = int(user_input) - 1
            if 0 <= option_num < len(self.context.options):
                selected_option = self.context.options[option_num]
        
        # Check if user entered an action name
        if not selected_option:
            user_input_lower = user_input.lower()
            for option in self.context.options:
                if option["action"].lower() == user_input_lower:
                    selected_option = option
                    break
                
                # Also check if the user entered part of the description
                if "description" in option and user_input_lower in option["description"].lower():
                    selected_option = option
                    break
        
        if selected_option:
            # Build command from the selected option
            command = {"action": selected_option["action"]}
            
            # Check if we need parameters
            if "required" in selected_option and selected_option["required"]:
                self.context.update(
                    state="missing_params",
                    command=command,
                    missing_params=selected_option["required"]
                )
                
                # Ask for the first missing parameter
                param = self.context.missing_params[0]
                message = f"Please provide the {param} for the {command['action']} command:"
                
                return {
                    "status": "missing_params",
                    "message": message,
                    "should_execute": False
                }
            else:
                # No parameters needed, execute the command
                self.context.update(
                    state="clear",
                    command=command
                )
                
                return {
                    "status": "clear",
                    "message": f"Executing command: {command['action']}",
                    "command": command,
                    "should_execute": True
                }
        else:
            # User didn't select a valid option
            options_text = "\n".join([f"{i+1}. {option.get('description', option['action'])}" 
                                   for i, option in enumerate(self.context.options[:5])])
            
            message = (
                f"I didn't understand your selection. "
                f"Please choose one of the following options by number or name:\n{options_text}"
            )
            
            return {
                "status": "ambiguous",
                "message": message,
                "should_execute": False
            }
    
    def _collect_parameters(self, user_input: str) -> Dict:
        """Collect missing parameters from user input."""
        if not self.context.missing_params:
            self.context.update(state="clear")
            return {
                "status": "clear",
                "message": f"Executing command: {self.context.command['action']}",
                "command": self.context.command,
                "should_execute": True
            }
        
        # Get the current parameter we're collecting
        current_param = self.context.missing_params[0]
        
        # Update the command with the provided parameter
        if not self.context.command:
            self.context.command = {}
        
        self.context.command[current_param] = user_input.strip()
        
        # Remove this parameter from the missing list
        self.context.missing_params.pop(0)
        
        # Check if we have all required parameters
        if not self.context.missing_params:
            # All parameters collected, ready to execute
            self.context.update(state="clear")
            
            return {
                "status": "clear",
                "message": f"Executing command: {self.context.command['action']}",
                "command": self.context.command,
                "should_execute": True
            }
        else:
            # Still missing parameters, ask for the next one
            next_param = self.context.missing_params[0]
            message = f"Please provide the {next_param} for the {self.context.command['action']} command:"
            
            return {
                "status": "missing_params",
                "message": message,
                "should_execute": False
            }
    
    def request_clarification(self, options: List[Dict]) -> Dict:
        """
        Request clarification when a command is ambiguous.
        
        Args:
            options: List of possible command options
            
        Returns:
            Dict with the clarification message
        """
        self.context.update(
            state="ambiguous",
            options=options
        )
        
        option_texts = []
        for i, option in enumerate(options[:5]):  # Limit to top 5
            desc = option.get("description", option["action"])
            option_texts.append(f"{i+1}. {desc}")
        
        options_text = "\n".join(option_texts)
        message = (
            f"I'm not sure which command you want to run. "
            f"Please choose one of the following options by number or name:\n{options_text}"
        )
        
        return {
            "status": "ambiguous",
            "message": message
        }
    
    def request_parameters(self, command: Dict) -> Dict:
        """
        Request missing parameters for a command.
        
        Args:
            command: Partial command dictionary
            
        Returns:
            Dict with the parameter request message
        """
        # Check command structure to determine missing parameters
        from .intent_parser import CommandRegistry
        
        registry = CommandRegistry()
        command_info = registry.get_command(command["action"])
        
        if not command_info or "required" not in command_info:
            # If we can't determine required parameters, just execute with what we have
            return {
                "status": "clear",
                "message": f"Executing command: {command['action']}",
                "command": command,
                "should_execute": True
            }
        
        # Find which required parameters are missing
        missing_params = []
        for param in command_info["required"]:
            if param not in command or not command[param]:
                missing_params.append(param)
        
        if not missing_params:
            # All required parameters are present
            return {
                "status": "clear",
                "message": f"Executing command: {command['action']}",
                "command": command,
                "should_execute": True
            }
        
        # Update context for parameter collection
        self.context.update(
            state="missing_params",
            command=command,
            missing_params=missing_params
        )
        
        # Ask for the first missing parameter
        param = missing_params[0]
        message = f"Please provide the {param} for the {command['action']} command:"
        
        return {
            "status": "missing_params",
            "message": message
        }
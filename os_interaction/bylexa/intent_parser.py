import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import importlib.util
import nltk
from nltk.tokenize import word_tokenize
import spacy
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class CommandRegistry:
    """Registry for available commands and their parameters."""
    
    def __init__(self):
        self.commands = {}
        self.aliases = {}
        self._load_builtin_commands()
        self._load_plugin_commands()
    
    def _load_builtin_commands(self):
        """Load built-in commands and their parameters."""
        # Define core commands with their parameters and aliases
        self.commands = {
            "open": {
                "params": ["application", "task", "file_path"],
                "required": ["application"],
                "description": "Open an application or file"
            },
            "script": {
                "params": ["script_name", "args", "parameters"],
                "required": ["script_name"],
                "description": "Run a custom script"
            },
            "run": {
                "params": ["command_line"],
                "required": ["command_line"],
                "description": "Execute a shell command"
            },
            "file": {
                "params": ["file_action", "source", "destination"],
                "required": ["file_action", "source"],
                "description": "Perform file operations"
            },
            "clipboard": {
                "params": ["clipboard_action", "text"],
                "required": ["clipboard_action"],
                "description": "Interact with clipboard"
            },
            "media": {
                "params": ["media_action", "media", "seek_time", "volume_level"],
                "required": ["media_action"],
                "description": "Control media playback"
            },
            "close": {
                "params": ["application"],
                "required": ["application"],
                "description": "Close an application"
            }
        }
        
        # Define aliases for commands and actions
        self.aliases = {
            # Command aliases
            "launch": "open",
            "start": "open",
            "execute": "run",
            "copy": "clipboard",
            "paste": "clipboard",
            "play": "media",
            "pause": "media",
            "volume": "media",
            
            # Parameter value aliases
            "chrome": ["chrome", "google chrome", "browser"],
            "word": ["word", "microsoft word", "ms word", "document editor"],
            "copy_action": ["copy", "duplicate"],
            "move_action": ["move", "relocate"],
            "delete_action": ["delete", "remove"],
            "play_action": ["play", "start playback", "resume"],
            "pause_action": ["pause", "stop playback"],
        }
    
    def _load_plugin_commands(self):
        """Load commands from installed plugins."""
        try:
            # Import plugin_manager only when needed to avoid circular imports
            from .plugins import plugin_manager
            
            for plugin_id, plugin in plugin_manager.plugins.items():
                if not plugin['enabled']:
                    continue
                
                # Check if the plugin defines commands
                if hasattr(plugin['module'], 'get_commands'):
                    try:
                        plugin_commands = plugin['module'].get_commands()
                        for cmd_name, cmd_info in plugin_commands.items():
                            self.commands[f"{plugin_id}.{cmd_name}"] = cmd_info
                    except Exception as e:
                        logger.error(f"Error loading commands from plugin {plugin_id}: {e}")
                
                # Check if the plugin defines aliases
                if hasattr(plugin['module'], 'get_aliases'):
                    try:
                        plugin_aliases = plugin['module'].get_aliases()
                        for alias, target in plugin_aliases.items():
                            self.aliases[alias] = target
                    except Exception as e:
                        logger.error(f"Error loading aliases from plugin {plugin_id}: {e}")
        
        except ImportError:
            logger.warning("Plugin manager not available, skipping plugin commands.")
    
    def get_command(self, name: str) -> Optional[Dict]:
        """Get command details by name or alias."""
        # Check if this is a direct command name
        if name in self.commands:
            return {"action": name, **self.commands[name]}
        
        # Check if this is an alias
        if name in self.aliases:
            target = self.aliases[name]
            if isinstance(target, str) and target in self.commands:
                return {"action": target, **self.commands[target]}
        
        return None
    
    def get_similar_commands(self, name: str, threshold: float = 0.7) -> List[Dict]:
        """Get commands similar to the given name."""
        similar_commands = []
        
        # Check direct commands and their descriptions
        for cmd_name, cmd_info in self.commands.items():
            similarity = self._calculate_similarity(name, cmd_name)
            if similarity >= threshold:
                similar_commands.append({
                    "action": cmd_name,
                    "similarity": similarity,
                    **cmd_info
                })
            
            # Also check the description
            if "description" in cmd_info:
                desc_similarity = self._calculate_similarity(name, cmd_info["description"])
                if desc_similarity > similarity and desc_similarity >= threshold:
                    # Update the existing entry if we already added it
                    for i, cmd in enumerate(similar_commands):
                        if cmd["action"] == cmd_name:
                            similar_commands[i]["similarity"] = desc_similarity
                            break
                    else:
                        # Otherwise add a new entry
                        similar_commands.append({
                            "action": cmd_name,
                            "similarity": desc_similarity,
                            **cmd_info
                        })
        
        # Sort by similarity score descending
        similar_commands.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_commands
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate text similarity between two strings."""
        # Simple Jaccard similarity for now, could be enhanced
        set1 = set(str1.lower().split())
        set2 = set(str2.lower().split())
        
        if not set1 or not set2:
            return 0.0
            
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0


class IntentParser:
    """Parser for extracting intents from natural language commands."""
    
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """
        Initialize the intent parser.
        
        Args:
            spacy_model: Name of the spaCy model to load
        """
        self.command_registry = CommandRegistry()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load(spacy_model)
            logger.info(f"Loaded spaCy model: {spacy_model}")
        except OSError:
            logger.warning(f"spaCy model '{spacy_model}' not found. Downloading...")
            spacy.cli.download(spacy_model)
            self.nlp = spacy.load(spacy_model)
            logger.info(f"Downloaded and loaded spaCy model: {spacy_model}")
        
        # Load any additional models or resources
        self._load_models()
    
    def _load_models(self):
        """Load any additional models or embeddings needed."""
        # This could be extended to load tensorflow/pytorch models,
        # word embeddings, etc. as the system scales
        pass
    
    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language text into a structured command.
        
        Args:
            text: Natural language command text
            
        Returns:
            Dictionary with parsed command structure and status
        """
        logger.info(f"Parsing command: '{text}'")
        
        # Skip processing if text is empty
        if not text or text.strip() == "":
            return {"status": "error", "message": "Empty command"}
        
        # Process text with spaCy for NER, POS tagging, etc.
        doc = self.nlp(text)
        
        # Extract potential command/action
        command_action = self._extract_command_action(doc)
        logger.info(f"Extracted command action: {command_action}")
        
        if not command_action:
            # Try to find similar commands
            potential_commands = self._find_potential_commands(text)
            if potential_commands:
                return {
                    "status": "ambiguous", 
                    "options": potential_commands,
                    "original_text": text
                }
            else:
                return {
                    "status": "error", 
                    "message": "Could not identify a command",
                    "original_text": text
                }
        
        # Extract parameters for the command
        parameters = self._extract_parameters(doc, command_action)
        logger.info(f"Extracted parameters: {parameters}")
        
        # Validate the command structure
        validation_result = self._validate_command(command_action, parameters)
        
        if validation_result["valid"]:
            # Command is valid and complete
            return {
                "status": "clear",
                "command": {
                    "action": command_action,
                    **parameters
                },
                "original_text": text
            }
        elif validation_result["missing_params"]:
            # Command is valid but missing required parameters
            return {
                "status": "missing_params",
                "command": {
                    "action": command_action,
                    **parameters
                },
                "missing_params": validation_result["missing_params"],
                "original_text": text
            }
        else:
            # Command is invalid
            return {
                "status": "error", 
                "message": validation_result["message"],
                "original_text": text
            }
    
    def _extract_command_action(self, doc) -> Optional[str]:
        """Extract the main command or action from the parsed document."""
        # Start with verb detection as commands often start with verbs
        main_verb = None
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ in ["ROOT", "ccomp", "xcomp"]:
                main_verb = token.lemma_
                break
        
        # If no main verb found, look for the first word as a potential command
        if not main_verb and len(doc) > 0:
            main_verb = doc[0].lemma_
        
        # Check if the verb or first word is a recognized command
        if main_verb:
            command = self.command_registry.get_command(main_verb)
            if command:
                return command["action"]
            
            # Check for multi-word commands (e.g., "play music", "open browser")
            for i in range(1, min(4, len(doc))):
                if i < len(doc):
                    multi_word = f"{main_verb} {doc[i].lemma_}"
                    command = self.command_registry.get_command(multi_word)
                    if command:
                        return command["action"]
        
        # If still not found, try checking for any token that might be a command
        for token in doc:
            command = self.command_registry.get_command(token.lemma_)
            if command:
                return command["action"]
        
        return None
    
    def _extract_parameters(self, doc, command_action: str) -> Dict[str, Any]:
        """Extract parameters for the given command from the parsed document."""
        parameters = {}
        
        # Get command details to know what parameters to look for
        command_info = self.command_registry.get_command(command_action)
        if not command_info or "params" not in command_info:
            return parameters
        
        # Extract parameters based on the command type
        if command_action == "open":
            # For "open" commands, look for application names and tasks
            app_name = None
            task = None
            
            # Look for direct objects which could be the application
            for token in doc:
                if token.dep_ == "dobj" and not app_name:
                    app_name = token.text
                    break
            
            # If no direct object, look for nouns after the verb
            if not app_name:
                verb_found = False
                for token in doc:
                    if verb_found and token.pos_ in ["NOUN", "PROPN"]:
                        app_name = token.text
                        break
                    if token.lemma_ == "open":
                        verb_found = True
            
            # Look for prepositional phrases that might contain the task
            for token in doc:
                if token.dep_ == "prep" and token.head.lemma_ == "open":
                    for child in token.children:
                        if child.dep_ == "pobj":
                            task = child.text
                            break
            
            if app_name:
                parameters["application"] = app_name
            if task:
                parameters["task"] = task
        
        elif command_action == "media":
            # For media commands, determine the specific media action
            media_action = None
            
            # Check for specific media verbs
            media_verbs = {
                "play": "play", "start": "play", "resume": "play",
                "pause": "pause", "stop": "pause",
                "next": "next", "previous": "previous", "skip": "next",
                "mute": "mute", "unmute": "unmute",
                "increase": "volume_up", "decrease": "volume_down", 
                "turn up": "volume_up", "turn down": "volume_down"
            }
            
            for verb, action in media_verbs.items():
                if verb in doc.text.lower():
                    media_action = action
                    break
            
            # Look for volume level specifications
            volume_level = None
            volume_pattern = re.search(r'(\d+)(?:\s*%|\s*percent)', doc.text)
            if volume_pattern:
                try:
                    volume_level = int(volume_pattern.group(1))
                    media_action = "volume"
                except ValueError:
                    pass
            
            if media_action:
                parameters["media_action"] = media_action
            if volume_level is not None:
                parameters["volume_level"] = volume_level
        
        elif command_action == "file":
            # For file commands, determine the file action and paths
            file_action = None
            source = None
            destination = None
            
            # Map verbs to file actions
            file_verbs = {
                "copy": "copy", "duplicate": "copy",
                "move": "move", "relocate": "move", 
                "delete": "delete", "remove": "delete",
                "create": "create_directory", "make": "create_directory"
            }
            
            for verb, action in file_verbs.items():
                if verb in doc.text.lower():
                    file_action = action
                    break
            
            # Extract file paths - this is a simplified version
            # Real implementation would need to handle quoted paths, etc.
            path_pattern = re.findall(r'["\'](.*?)["\']|(\S+\.\S+)', doc.text)
            paths = [match[0] or match[1] for match in path_pattern if match[0] or match[1]]
            
            if paths:
                source = paths[0]
                if len(paths) > 1 and file_action in ["copy", "move"]:
                    destination = paths[1]
            
            if file_action:
                parameters["file_action"] = file_action
            if source:
                parameters["source"] = source
            if destination:
                parameters["destination"] = destination
        
        # Add more specialized parameter extraction for other command types
        
        return parameters
    
    def _validate_command(self, command_action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the command has all required parameters.
        
        Returns:
            Dictionary with validation results
        """
        command_info = self.command_registry.get_command(command_action)
        if not command_info:
            return {
                "valid": False,
                "message": f"Unknown command: {command_action}"
            }
        
        # Check for required parameters
        missing_params = []
        if "required" in command_info:
            for param in command_info["required"]:
                if param not in parameters:
                    missing_params.append(param)
        
        if missing_params:
            return {
                "valid": False,
                "missing_params": missing_params,
                "message": f"Missing required parameters: {', '.join(missing_params)}"
            }
        
        return {"valid": True}
    
    def _find_potential_commands(self, text: str) -> List[Dict]:
        """Find potential commands based on the input text."""
        # Tokenize the text
        tokens = word_tokenize(text.lower())
        
        # Get potential commands based on individual tokens
        potential_commands = []
        for token in tokens:
            similar_commands = self.command_registry.get_similar_commands(token)
            potential_commands.extend(similar_commands)
        
        # Also try the full text for multi-word commands
        similar_commands = self.command_registry.get_similar_commands(text.lower())
        potential_commands.extend(similar_commands)
        
        # Remove duplicates and sort by similarity
        unique_commands = {}
        for cmd in potential_commands:
            action = cmd["action"]
            if action not in unique_commands or cmd["similarity"] > unique_commands[action]["similarity"]:
                unique_commands[action] = cmd
        
        return list(unique_commands.values())
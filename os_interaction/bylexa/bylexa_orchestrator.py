import os
import sys
import logging
import asyncio
import threading
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Bylexa components
from .ai_orchestrator import init_orchestrator, get_orchestrator
from .intent_parser import IntentParser
from .dialog_manager import DialogManager
from .websocket_gateway import start_ws_server, stop_ws_server
from .script_manager import init_script_manager
from .community_registry import get_registry
from .config import load_app_configs, load_token
from . import plugin_dev_kit as plugin_manager 
class BylexaOrchestrator:
    """
    Main orchestrator for the Bylexa system that initializes and manages
    all components and handles the lifecycle of the application.
    """
    
    def __init__(self):
        """Initialize the Bylexa orchestrator."""
        self.config = load_app_configs()
        self.running = False
        self.ws_task = None
        self.components_initialized = False
        self.plugins_dir = None
    
    def initialize_components(self):
        """Initialize all Bylexa components."""
        if self.components_initialized:
            return
        
        logger.info("Initializing Bylexa components...")
        
        # Initialize script manager
        scripts_dir = self.config.get('scripts_directory', 'scripts')
        init_script_manager(scripts_dir)
        logger.info(f"Script manager initialized with directory: {scripts_dir}")
        
        # Initialize community registry
        registry = get_registry()
        logger.info("Community registry initialized")
        
        # Initialize AI orchestrator
        orchestrator = init_orchestrator()
        logger.info("AI orchestrator initialized")
        
        # Load plugins
        self.plugins_dir = Path(self.config.get('plugins_directory', 'plugins'))
        plugins_dir = Path(self.config.get('plugins_directory', 'plugins'))
        if not plugins_dir.is_absolute():
            plugins_dir = Path.home() / '.bylexa' / plugins_dir
        
        # Proper instantiation
        self.plugin_manager = plugin_manager.PluginManager(plugins_dir)
        self.plugin_manager.load_all_plugins()
        logger.info(f"Loaded {len(self.plugin_manager.plugins)} plugins")
        logger.info(f"Plugins directory: {self.plugins_dir}")

        
        self.components_initialized = True
        logger.info("All components initialized successfully")
    
    async def start(self):
        """Start the Bylexa system."""
        if self.running:
            logger.warning("Bylexa is already running")
            return
        
        # Initialize components
        self.initialize_components()
        
        # Set running flag
        self.running = True
        
        # Start WebSocket server
        ws_host = self.config.get('ws_host', 'localhost')
        ws_port = int(self.config.get('ws_port', 8765))
        
        logger.info(f"Starting WebSocket server on {ws_host}:{ws_port}")
        try:
            self.ws_task = asyncio.create_task(start_ws_server(ws_host, ws_port))
            logger.info("WebSocket server started")
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {str(e)}")
            self.running = False
            return
        
        logger.info("Bylexa system started and running")
    
    async def stop(self):
        """Stop the Bylexa system."""
        if not self.running:
            logger.warning("Bylexa is not running")
            return
        
        logger.info("Stopping Bylexa system...")
        
        # Stop WebSocket server
        try:
            await stop_ws_server()
            if self.ws_task:
                self.ws_task.cancel()
                try:
                    await self.ws_task
                except asyncio.CancelledError:
                    pass
                self.ws_task = None
        except Exception as e:
            logger.error(f"Error stopping WebSocket server: {str(e)}")
        
        # Stop AI orchestrator
        try:
            orchestrator = get_orchestrator()
            orchestrator.stop()
        except Exception as e:
            logger.error(f"Error stopping AI orchestrator: {str(e)}")
        
        # Set running flag
        self.running = False
        logger.info("Bylexa system stopped")
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a command directly using the AI orchestrator.
        
        Args:
            command: Command string to process
            
        Returns:
            Response dictionary
        """
        # Initialize components if needed
        if not self.components_initialized:
            self.initialize_components()
        
        # Get AI orchestrator
        orchestrator = get_orchestrator()
        
        # Process the command
        result = orchestrator.process_text(command)
        
        # Wait for execution to complete
        while orchestrator.has_pending_commands():
            execution_result = orchestrator.get_execution_result(timeout=0.5)
            if execution_result:
                result['execution_result'] = execution_result
        
        return result


# Global orchestrator instance
_orchestrator_instance = None

def get_bylexa_orchestrator() -> BylexaOrchestrator:
    """Get the global Bylexa orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = BylexaOrchestrator()
    return _orchestrator_instance

async def main_async():
    """Main async entry point."""
    parser = argparse.ArgumentParser(description='Bylexa Orchestrator')
    parser.add_argument('--command', help='Command to execute')
    parser.add_argument('--start', action='store_true', help='Start Bylexa system')
    parser.add_argument('--stop', action='store_true', help='Stop Bylexa system')
    
    args = parser.parse_args()
    
    # Get orchestrator instance
    orchestrator = get_bylexa_orchestrator()
    
    if args.command:
        # Execute a single command
        result = orchestrator.process_command(args.command)
        print(json.dumps(result, indent=2))
    
    elif args.start:
        # Start the system
        await orchestrator.start()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1.0)
        except KeyboardInterrupt:
            print("\nShutting down...")
            await orchestrator.stop()
    
    elif args.stop:
        # Stop the system
        await orchestrator.stop()
    
    else:
        # No arguments, print usage
        parser.print_help()

def main():
    """Main entry point for the command line."""
    # Run the async main
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
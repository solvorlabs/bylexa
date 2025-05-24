import click
import asyncio
import json
import sys
import os
import time
from pathlib import Path
import logging
from typing import Dict, Any, Optional

from .my_token import login as do_login
from .websocket_client import start_client
from .config_gui import run_gui
from .bylexa_orchestrator import get_bylexa_orchestrator
from .community_registry import get_registry
from .script_sandbox import validate_script
from .ai_orchestrator import get_orchestrator

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@click.group()
def main():
    """Bylexa - AI-powered automation middleware"""
    pass

@main.command()
def login():
    """Login to Bylexa and store the token."""
    do_login()

@main.command()
def start():
    """Start the Bylexa system and listen for commands."""
    try:
        # Run in asyncio event loop
        asyncio.run(start_bylexa())
    except KeyboardInterrupt:
        print("\nStopping Bylexa system...")
        # Clean shutdown
        asyncio.run(stop_bylexa())
    except Exception as e:
        logger.error(f"Error starting Bylexa: {str(e)}")
        sys.exit(1)

@main.command()
def stop():
    """Stop the Bylexa system."""
    try:
        asyncio.run(stop_bylexa())
        print("Bylexa system stopped")
    except Exception as e:
        logger.error(f"Error stopping Bylexa: {str(e)}")
        sys.exit(1)

@main.command()
def config():
    """Open the Bylexa configuration GUI."""
    run_gui()

@main.command()
@click.argument('command', nargs=-1)
def exec(command):
    """Execute a command directly."""
    # Join command parts into a single string
    cmd_str = ' '.join(command)
    
    if not cmd_str:
        print("Error: Command required")
        sys.exit(1)
    
    try:
        # Process command
        orchestrator = get_bylexa_orchestrator()
        orchestrator.initialize_components()
        
        result = orchestrator.process_command(cmd_str)
        
        # Print the result
        if isinstance(result, dict) and 'message' in result:
            print(f"Response: {result['message']}")
            
            if 'execution_result' in result:
                print(f"Execution result: {result['execution_result']}")
            
            if result.get('status') == 'error':
                sys.exit(1)
        else:
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        sys.exit(1)

@main.command()
@click.argument('query', required=False)
def search(query):
    """Search for scripts in the community registry."""
    try:
        registry = get_registry()
        results = registry.search_scripts(query or "")
        
        if not results:
            print("No scripts found")
            return
        
        print(f"Found {len(results)} scripts:")
        for i, script in enumerate(results):
            print(f"{i+1}. {script.get('name')} (by {script.get('author', 'unknown')})")
            print(f"   Description: {script.get('description', 'No description')}")
            print(f"   Version: {script.get('version', 'N/A')}")
            if 'remote_only' in script and script['remote_only']:
                print("   [Available in remote registry]")
            print()

    except Exception as e:
        logger.error(f"Error searching scripts: {str(e)}")
        sys.exit(1)

@main.command()
@click.argument('script_id')
def install(script_id):
    """Install a script from the community registry."""
    try:
        registry = get_registry()
        result = registry.download_script(script_id=script_id)
        
        if result.get('status') == 'success':
            print(f"Successfully installed script: {result.get('script_data', {}).get('name', script_id)}")
        else:
            print(f"Error installing script: {result.get('message', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error installing script: {str(e)}")
        sys.exit(1)

@main.command()
@click.argument('script_path')
def validate(script_path):
    """Validate a script file."""
    if not os.path.exists(script_path):
        print(f"Error: Script file not found: {script_path}")
        sys.exit(1)
    
    try:
        print(f"Validating script: {script_path}")
        result = validate_script(script_path)
        
        if result.get('success'):
            print("Validation successful!")
            if result.get('output'):
                print("\nOutput:")
                print(result['output'])
        else:
            print("Validation failed!")
            if result.get('errors'):
                print("\nErrors:")
                print(result['errors'])
            if result.get('exception'):
                print("\nException:")
                print(f"Type: {result['exception']['type']}")
                print(f"Message: {result['exception']['message']}")
                print(f"Traceback: {result['exception']['traceback']}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error validating script: {str(e)}")
        sys.exit(1)

@main.command()
@click.argument('script_path')
@click.argument('metadata_path')
def publish(script_path, metadata_path):
    """Publish a script to the community registry."""
    if not os.path.exists(script_path):
        print(f"Error: Script file not found: {script_path}")
        sys.exit(1)
    
    if not os.path.exists(metadata_path):
        print(f"Error: Metadata file not found: {metadata_path}")
        sys.exit(1)
    
    try:
        # Read script file
        with open(script_path, 'r') as f:
            script_code = f.read()
        
        # Read metadata file
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Add script code to metadata
        metadata['source'] = script_code
        
        # Validate script
        print(f"Validating script: {script_path}")
        result = validate_script(script_path)
        
        if not result.get('success'):
            print("Validation failed!")
            if result.get('errors'):
                print("\nErrors:")
                print(result['errors'])
            if result.get('exception'):
                print("\nException:")
                print(f"Type: {result['exception']['type']}")
                print(f"Message: {result['exception']['message']}")
                sys.exit(1)
        
        # Publish script
        registry = get_registry()
        result = registry.submit_script(metadata)
        
        if result.get('status') in ('success', 'partial'):
            print(f"Successfully published script: {metadata.get('name')}")
            if result.get('status') == 'partial':
                print(f"Warning: {result.get('message', 'Unknown warning')}")
        else:
            print(f"Error publishing script: {result.get('message', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error publishing script: {str(e)}")
        sys.exit(1)

@main.command()
@click.argument('text')
def parse(text):
    """Parse a natural language command for testing."""
    try:
        # Initialize AI components
        orchestrator = get_bylexa_orchestrator()
        orchestrator.initialize_components()
        
        # Get AI orchestrator
        ai = get_orchestrator()
        
        # Parse the text
        print(f"Parsing text: {text}")
        result = ai.parser.parse_command(text)
        
        # Print the result
        print(json.dumps(result, indent=2))
    
    except Exception as e:
        logger.error(f"Error parsing command: {str(e)}")
        sys.exit(1)

@main.command()
def client():
    """Start the WebSocket client."""
    try:
        start_client()
    except KeyboardInterrupt:
        print("\nStopping client...")
    except Exception as e:
        logger.error(f"Error in client: {str(e)}")
        sys.exit(1)

async def start_bylexa():
    """Start the Bylexa system."""
    orchestrator = get_bylexa_orchestrator()
    await orchestrator.start()
    
    print("Bylexa system started")
    print("Press Ctrl+C to stop")
    
    # Keep running until interrupted
    while True:
        await asyncio.sleep(1.0)

async def stop_bylexa():
    """Stop the Bylexa system."""
    orchestrator = get_bylexa_orchestrator()
    await orchestrator.stop()

if __name__ == "__main__":
    main()
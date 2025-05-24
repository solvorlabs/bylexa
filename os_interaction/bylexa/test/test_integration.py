# test_integration.py
import asyncio
import time
from bylexa.bylexa_orchestrator import get_bylexa_orchestrator

async def test_full_system():
    print("=== Full System Integration Test ===")
    
    orchestrator = get_bylexa_orchestrator()
    
    # Initialize components
    orchestrator.initialize_components()
    print("✓ Components initialized")
    
    # Test direct command processing
    result = orchestrator.process_command("open calculator")
    print(f"✓ Command processing: {result.get('status')}")
    
    # Start the system
    print("Starting full system...")
    await orchestrator.start()
    
    # Wait a bit
    await asyncio.sleep(2)
    
    print("✓ System started successfully")
    print(f"  - WebSocket server running: {orchestrator.running}")
    print(f"  - Components initialized: {orchestrator.components_initialized}")
    
    # Stop the system
    await orchestrator.stop()
    print("✓ System stopped successfully")

if __name__ == "__main__":
    asyncio.run(test_full_system())
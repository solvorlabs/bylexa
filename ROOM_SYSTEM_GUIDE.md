# Bylexa Room System - Complete Guide

## Overview

The Room System allows multiple users to collaborate and share computational resources in real-time. It's designed to work like a distributed Jupyter notebook where users can execute code on remote machines.

## Architecture

### Components

1. **WebSocket Server** (`server/config/websocket.js`)
   - Manages room creation and membership
   - Routes messages between room participants
   - Tracks machine information and capabilities

2. **Python Client** (`os_interaction/bylexa/websocket_client.py`)
   - Connects to the WebSocket server
   - Receives and executes commands
   - Reports machine capabilities

3. **Machine Registry** (`os_interaction/bylexa/machine_registry.py`)
   - Collects machine information (CPU, RAM, OS, etc.)
   - Detects capabilities (Python packages, GPU, etc.)
   - Generates unique machine ID

## Key Features

### 1. Machine Registration

When a client connects, it automatically registers its machine information:

```python
{
  "machine_id": "hostname-mac_address",
  "machine_data": {
    "os": "Windows/Linux/Darwin",
    "platform": "Windows-10-...",
    "hostname": "my-computer",
    "cpu_count": 8,
    "memory_total": 16000000000,
    "memory_available": 8000000000,
    "capabilities": ["python", "windows", "selenium", "numpy", "cuda"]
  }
}
```

### 2. Room Management

#### Creating/Joining a Room

```javascript
// Send join room message
{
  "action": "join_room",
  "room_code": "ABC123"
}

// Receive confirmation
{
  "action": "room_joined",
  "room_code": "ABC123",
  "message": "Joined room ABC123"
}
```

#### Leaving a Room

```javascript
{
  "action": "leave_room"
}
```

### 3. Listing Available Machines

Get a list of all machines in the current room:

```javascript
// Request
{
  "action": "list_machines"
}

// Response
{
  "action": "machines_list",
  "room_code": "ABC123",
  "machines": [
    {
      "email": "user1@example.com",
      "machineId": "computer1-123456",
      "os": "Windows",
      "cpu_count": 8,
      "memory_total": 16000000000,
      "capabilities": ["python", "windows", "cuda", "tensorflow"]
    },
    {
      "email": "user2@example.com",
      "machineId": "server1-789012",
      "os": "Linux",
      "cpu_count": 32,
      "memory_total": 64000000000,
      "capabilities": ["python", "linux", "pytorch", "gpu"]
    }
  ]
}
```

### 4. Targeted Command Execution

#### Execute Python Code on Specific Machines

```javascript
{
  "action": "python_execute",
  "code": "import platform; print(platform.machine())",
  "target_machines": ["computer1-123456", "server1-789012"]
}
```

If `target_machines` is omitted or empty, the code will be broadcast to ALL machines in the room.

#### Broadcast Commands

```javascript
{
  "action": "broadcast",
  "command": "open chrome",
  "target_machines": ["computer1-123456"]  // Optional
}
```

#### Notebook-style Execution

```javascript
{
  "action": "notebook_execute",
  "code": "import numpy as np; np.random.rand(5)",
  "cell_id": "cell-1",
  "target_machines": ["server1-789012"]  // Machine with numpy installed
}
```

## Use Cases

### 1. Distributed Computing

Execute computationally intensive tasks on machines with better resources:

```python
# On your local machine
send_to_room({
  "action": "python_execute",
  "code": """
import numpy as np
result = np.random.rand(10000, 10000)
print(f'Matrix created: {result.shape}')
  """,
  "target_machines": ["gpu-server-123456"]  # High-memory server
})
```

### 2. Multi-OS Testing

Test scripts on different operating systems simultaneously:

```python
# Get all machines
machines = get_machines_in_room()

# Filter by OS
windows_machines = [m for m in machines if 'windows' in m['os'].lower()]
linux_machines = [m for m in machines if 'linux' in m['os'].lower()]

# Execute test on Windows machines
send_to_room({
  "action": "python_execute",
  "code": "import os; print(os.name)",
  "target_machines": [m['machineId'] for m in windows_machines]
})

# Execute test on Linux machines
send_to_room({
  "action": "python_execute",
  "code": "import os; print(os.name)",
  "target_machines": [m['machineId'] for m in linux_machines]
})
```

### 3. Resource-Aware Task Distribution

Select machines based on available resources:

```python
# Get machines with CUDA support
gpu_machines = [m for m in machines if 'cuda' in m['capabilities']]

if gpu_machines:
  # Run deep learning training on GPU machines
  send_to_room({
    "action": "python_execute",
    "code": "import tensorflow as tf; tf.test.is_gpu_available()",
    "target_machines": [gpu_machines[0]['machineId']]
  })
```

### 4. Collaborative Development

Multiple developers can share a room and execute code on each other's machines:

```python
# Developer A's machine has a specific database setup
# Developer B can test queries on it remotely
send_to_room({
  "action": "python_execute",
  "code": """
import sqlite3
conn = sqlite3.connect('test.db')
result = conn.execute('SELECT COUNT(*) FROM users').fetchone()
print(f'User count: {result[0]}')
  """,
  "target_machines": ["developer-a-machine-id"]
})
```

## WebSocket API Reference

### Client → Server Messages

#### Register Machine

```json
{
  "action": "register_machine",
  "machine_id": "unique-machine-id",
  "machine_data": {
    "os": "string",
    "platform": "string",
    "hostname": "string",
    "cpu_count": 8,
    "memory_total": 16000000000,
    "memory_available": 8000000000,
    "capabilities": ["python", "numpy"]
  }
}
```

**Response:**
```json
{
  "action": "machine_registered",
  "machine_id": "unique-machine-id",
  "message": "Machine successfully registered"
}
```

#### Join Room

```json
{
  "action": "join_room",
  "room_code": "ABC123"
}
```

**Response:**
```json
{
  "action": "room_joined",
  "room_code": "ABC123",
  "message": "Joined room ABC123"
}
```

**Broadcast to Others:**
```json
{
  "action": "user_joined",
  "message": "user@example.com has joined the room",
  "user": "user@example.com"
}
```

#### List Machines

```json
{
  "action": "list_machines"
}
```

**Response:**
```json
{
  "action": "machines_list",
  "room_code": "ABC123",
  "machines": [...]
}
```

#### Execute Python Code

```json
{
  "action": "python_execute",
  "code": "print('Hello')",
  "target_machines": ["machine-id-1", "machine-id-2"]
}
```

**Received by Target:**
```json
{
  "action": "python_execute",
  "code": "print('Hello')",
  "sender": "sender@example.com",
  "machine_id": "machine-id-1"
}
```

#### Send Execution Result

```json
{
  "action": "python_output",
  "result": {
    "stdout": "Hello\n",
    "stderr": "",
    "success": true
  },
  "code": "print('Hello')",
  "original_sender": "sender@example.com"
}
```

#### Broadcast Message

```json
{
  "action": "broadcast",
  "command": "some command",
  "target_machines": ["machine-id-1"]
}
```

#### Leave Room

```json
{
  "action": "leave_room"
}
```

**Response:**
```json
{
  "action": "room_left",
  "message": "Successfully left the room"
}
```

### Server → Client Messages

#### Machine Joined Notification

```json
{
  "action": "machine_joined",
  "machine_id": "new-machine-id",
  "machine_data": {...},
  "user": "user@example.com"
}
```

#### Execution Request

```json
{
  "action": "python_execute",
  "code": "import platform; print(platform.machine())",
  "sender": "requester@example.com",
  "machine_id": "your-machine-id"
}
```

#### Execution Result

```json
{
  "action": "python_result",
  "result": {...},
  "executor": "executor@example.com",
  "code": "..."
}
```

## Implementation Example

### Python Client Side

```python
import asyncio
import websockets
import json
from bylexa.machine_registry import get_machine_registry

async def connect_and_register():
    # Get machine registry
    registry = get_machine_registry()

    # Connect to server
    uri = "ws://localhost:3000/ws"
    headers = {"Authorization": f"Bearer {your_jwt_token}"}

    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Send registration message
        reg_message = registry.get_registration_message()
        await websocket.send(json.dumps(reg_message))

        # Wait for confirmation
        response = await websocket.recv()
        print(f"Registration response: {response}")

        # Join a room
        await websocket.send(json.dumps({
            "action": "join_room",
            "room_code": "DEMO-ROOM"
        }))

        # Wait for room join confirmation
        response = await websocket.recv()
        print(f"Room join response: {response}")

        # List machines in room
        await websocket.send(json.dumps({
            "action": "list_machines"
        }))

        # Get machines list
        response = await websocket.recv()
        machines = json.loads(response)
        print(f"Machines in room: {machines}")

        # Execute code on specific machine
        if machines['machines']:
            target_machine = machines['machines'][0]['machineId']
            await websocket.send(json.dumps({
                "action": "python_execute",
                "code": "import platform; print(platform.system())",
                "target_machines": [target_machine]
            }))

        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data['action'] == 'python_execute':
                # Execute the code
                code = data['code']
                sender = data['sender']

                try:
                    # Execute Python code
                    result = exec(code)

                    # Send result back
                    await websocket.send(json.dumps({
                        "action": "python_output",
                        "result": {"success": True, "output": str(result)},
                        "code": code,
                        "original_sender": sender
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        "action": "python_output",
                        "result": {"success": False, "error": str(e)},
                        "code": code,
                        "original_sender": sender
                    }))

# Run the client
asyncio.run(connect_and_register())
```

### Web Client Side (JavaScript)

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:3000/ws', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Send machine registration (if applicable for web client)
ws.onopen = () => {
  // Join room
  ws.send(JSON.stringify({
    action: 'join_room',
    room_code: 'DEMO-ROOM'
  }));
};

// List machines in room
function listMachines() {
  ws.send(JSON.stringify({
    action: 'list_machines'
  }));
}

// Execute code on specific machine
function executeOnMachine(machineId, code) {
  ws.send(JSON.stringify({
    action: 'python_execute',
    code: code,
    target_machines: [machineId]
  }));
}

// Listen for messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.action) {
    case 'machines_list':
      console.log('Available machines:', data.machines);
      displayMachines(data.machines);
      break;

    case 'python_result':
      console.log('Execution result:', data.result);
      displayResult(data.result);
      break;

    case 'machine_joined':
      console.log('New machine joined:', data.machine_data);
      addMachineToList(data.machine_data);
      break;
  }
};

// Display machines in UI
function displayMachines(machines) {
  const machineList = document.getElementById('machine-list');
  machineList.innerHTML = '';

  machines.forEach(machine => {
    const div = document.createElement('div');
    div.className = 'machine-card';
    div.innerHTML = `
      <h3>${machine.hostname}</h3>
      <p>OS: ${machine.os}</p>
      <p>CPU: ${machine.cpu_count} cores</p>
      <p>RAM: ${(machine.memory_total / 1e9).toFixed(2)} GB</p>
      <p>Capabilities: ${machine.capabilities.join(', ')}</p>
      <button onclick="selectMachine('${machine.machineId}')">
        Select
      </button>
    `;
    machineList.appendChild(div);
  });
}
```

## Best Practices

### 1. Always Register Machine on Connect

```python
# Immediately after connection
registry = get_machine_registry()
await websocket.send(json.dumps(registry.get_registration_message()))
```

### 2. Check Machine Capabilities Before Execution

```python
# Before sending code requiring specific packages
machines_with_numpy = [m for m in machines if 'numpy' in m['capabilities']]
if machines_with_numpy:
    execute_on(machines_with_numpy[0]['machineId'], numpy_code)
else:
    print("No machines with numpy available")
```

### 3. Handle Execution Errors Gracefully

```python
try:
    result = execute_code(code)
    send_result(success=True, output=result)
except Exception as e:
    send_result(success=False, error=str(e))
```

### 4. Monitor Resource Usage

```python
# Before executing heavy tasks
resources = registry.get_current_resources()
if resources['memory_percent'] < 80 and resources['cpu_percent'] < 80:
    execute_task()
else:
    print("Machine resources are currently limited")
```

## Security Considerations

1. **Authentication**: All connections require valid JWT tokens
2. **Code Execution**: Only trusted users should be in the same room
3. **Resource Limits**: Consider implementing execution timeouts
4. **Sandboxing**: Consider using restricted execution environments
5. **Room Privacy**: Room codes should be shared securely

## Troubleshooting

### Machine Not Appearing in Room

1. Check if machine registration was successful
2. Verify room code is correct
3. Check network connectivity
4. Review server logs for errors

### Code Not Executing on Target Machine

1. Verify target machine ID is correct
2. Check if target machine is still in the room
3. Ensure target machine has required capabilities
4. Check for execution errors in logs

### Performance Issues

1. Limit number of simultaneous executions
2. Use targeted execution instead of broadcasting
3. Monitor network bandwidth
4. Implement result caching where appropriate

## Future Enhancements

1. **Load Balancing**: Automatically distribute tasks based on resource availability
2. **Queue Management**: Queue tasks when machines are busy
3. **Result Caching**: Cache results for repeated executions
4. **Machine Pools**: Create groups of machines for specific task types
5. **Resource Reservation**: Reserve machines for exclusive use
6. **Execution History**: Track what was executed on each machine
7. **Real-time Monitoring**: Monitor machine resources in real-time
8. **Auto-scaling**: Automatically add/remove machines from pool

## Conclusion

The enhanced Room System transforms Bylexa into a distributed computing platform where users can leverage computational resources across multiple machines. By implementing machine registration and targeted execution, users have fine-grained control over where and how their code executes.

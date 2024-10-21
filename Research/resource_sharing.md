Yes, you can absolutely set up a system where multiple PCs or devices connect to a server using sockets, and you distribute the computing tasks across these devices (also known as distributed computing). This method can be used to share computing resources across multiple machines (clients), allowing you to offload tasks and utilize their computational power.

### Key Components for This Setup

1. **Server**:
   - Acts as a central point that distributes tasks (code) to multiple connected clients.
   - Receives results from clients after computation.

2. **Clients**:
   - Multiple PCs/devices connected to the server over a network via sockets.
   - Each client receives code, executes it, and sends the results back to the server.

3. **Sockets**:
   - Used for communication between the server and clients.
   - The server sends code or tasks, and clients send back results.

4. **Task Management**:
   - The server manages task distribution to connected clients.
   - Clients perform computation on the received tasks and return results.

5. **Distributed Computing**:
   - By using multiple clients, you can distribute computational tasks, making it possible to leverage their computing power as if it were a cloud environment.

### Key Libraries to Use in Python:
- **`socket`**: For socket-based communication.
- **`pickle` or `json`**: For serializing and deserializing data (code, results) to send over the socket.
- **`multiprocessing` or `concurrent.futures`**: On the client side for running the received code in parallel.

### High-Level Steps:

1. **Server Setup**:
   - Start a socket server that listens for incoming client connections.
   - Distribute code/tasks to each connected client.
   - Gather results from clients.

2. **Client Setup**:
   - Each client connects to the server.
   - Receive code or tasks, execute them, and send the results back to the server.

3. **Code Distribution**:
   - You can either send Python code as a string or a serialized function.
   - The clients execute the code and return results.

### Example Code for Distributed Computing Using Sockets:

#### 1. Server Code:
The server will send tasks to multiple clients and gather their responses.

```python
import socket
import pickle  # or use json
import threading

clients = []  # Keep track of connected clients

# Function to handle each client separately
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} established!")
    
    # Send code or task to the client
    code = """
def compute(data):
    return sum(data)  # Example task, summing a list of numbers
"""
    client_socket.send(pickle.dumps(code))  # Send the code to the client
    
    # Receive the result from the client
    result = pickle.loads(client_socket.recv(4096))
    print(f"Received result from {client_address}: {result}")
    
    client_socket.close()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(5)  # Max 5 connections
    
    print("Server listening on port 9999...")
    
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        
        # Handle client in a new thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

if __name__ == "__main__":
    server()
```

#### 2. Client Code:
The client connects to the server, receives the task, executes it, and sends the result back.

```python
import socket
import pickle  # or use json

def run_code_locally(code_str, data):
    # Execute the code received from the server
    local_namespace = {}
    exec(code_str, {}, local_namespace)  # Dangerous, use carefully
    compute_func = local_namespace.get("compute")
    if compute_func:
        result = compute_func(data)
        return result
    return None

def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('your_server_ip', 9999))
    
    # Receive the code from the server
    code = pickle.loads(client_socket.recv(4096))
    
    # Example data that the client is working on
    data = [1, 2, 3, 4, 5]  # This could vary per client
    
    # Run the code with the data
    result = run_code_locally(code, data)
    
    # Send the result back to the server
    client_socket.send(pickle.dumps(result))
    
    client_socket.close()

if __name__ == "__main__":
    client()
```

### Explanation:

- **Server**:
  - Listens for incoming connections.
  - Sends a piece of code (a Python function in this example) to each client.
  - Receives the results after the clients execute the code.

- **Client**:
  - Connects to the server and receives code in the form of a string.
  - Executes the received code locally with specific data (the data can be dynamic per client).
  - Sends the result back to the server.

### How This Approach Works:

1. **Server as the Orchestrator**: The server distributes different parts of the code or tasks to each connected client. Each client can work on a different subset of data or perform a different task.
   
2. **Client as the Worker**: Each client receives code, executes it with specific data, and returns the result. The client can run any complex computation (e.g., machine learning training, numerical simulations, etc.).

3. **Parallel Execution**: You can distribute a large computation task across multiple clients, each performing its part in parallel. For example, if you are training a machine learning model, each client can work on different data batches and send the results back to the server.

4. **Use Cases**: This architecture is useful for:
   - Distributed data processing.
   - Offloading tasks to multiple machines.
   - Utilizing the combined CPU or GPU power of several devices for intensive tasks (like image processing, machine learning, or scientific simulations).

### Scaling the System:

- **Task Scheduling**: You can implement more advanced task scheduling to divide large tasks into smaller chunks and assign them to different clients.
- **Load Balancing**: To balance the workload among clients, you can use a load balancer, ensuring that each client gets a fair amount of tasks.
- **Fault Tolerance**: Implement error handling so if a client fails, the server can reassign the task to another client.

### Considerations:
- **Security**: `exec()` can be dangerous because it allows arbitrary code execution. You need to sanitize the input or implement security measures, especially if you don't control the clients.
- **Network Latency**: If clients are geographically distant from the server, network latency could be a limiting factor in performance.
- **Scalability**: As the number of clients grows, managing and balancing workload distribution becomes important.

### Summary:

Yes, you can use sockets to distribute computational tasks across multiple devices (clients) and share their computing resources for running code remotely. The server distributes the tasks, and the clients execute the code and return the results. This setup can simulate cloud-like distributed computing, where you take advantage of the combined processing power of multiple devices.

For more advanced distributed computing, you might look into frameworks like **Dask**, **Ray**, or **Celery**, but the socket-based approach described above gives you more control and flexibility over how tasks are distributed and processed.
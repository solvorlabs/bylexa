const WebSocket = require('ws');
const jwt = require('jsonwebtoken');

// Secret key used to decode the JWT token
const JWT_SECRET = 'bylexa';

// Store connected clients by email
const clients = {};

// Store rooms and their participants
const rooms = {};

// Store machine information for each client
const machineInfo = {};

// Setup the WebSocket server
const setupWebSocket = (server) => {
  const wss = new WebSocket.Server({ server, path: '/ws' });

  wss.on('connection', (ws, req) => {
    const token = req.headers['authorization'].split(' ')[1];

    let email;
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      email = decoded.email;
    } catch (error) {
      console.log('Invalid token. Closing connection.');
      ws.close();
      return;
    }

    if (email) {
      clients[email] = { ws, room: null, machineId: null };
      console.log(`User with email ${email} connected`);

      ws.on('message', async (message) => {
        try {
          const parsedMessage = JSON.parse(message.toString());
          console.log('Received message:', parsedMessage);

          switch (parsedMessage.action) {
            case 'register_machine':
              handleMachineRegistration(email, parsedMessage, ws);
              break;

            case 'join_room':
              handleJoinRoom(email, parsedMessage, ws);
              break;

            case 'broadcast':
              handleBroadcast(email, parsedMessage);
              break;

            case 'show_notification':
              handleNotification(email, parsedMessage);
              break;

            case 'python_output':
              handlePythonOutput(email, parsedMessage);
              break;
            case 'python_execute':
              handlePythonExecution(email, parsedMessage);
              break;

            case 'direct_message':
              handleDirectMessage(email, parsedMessage);
              break;

            case 'leave_room':
              handleLeaveRoom(email, parsedMessage);
              break;

            case 'notebook_execute':
              handleNotebookExecution(email, parsedMessage);
              break;

            case 'notebook_result':
              handleNotebookResult(email, parsedMessage);
              break;

            case 'list_machines':
              handleListMachines(email, parsedMessage, ws);
              break;

            case 'save_notebook':
              // Forward save request to the executing client
              const roomCode = clients[email]?.room;
              if (roomCode) {
                broadcastToRoom(roomCode, email, {
                  action: 'save_notebook',
                  sender: email
                });
              }
              break;
              
            default:
              console.log(`Unknown action type from ${email}:`, parsedMessage);
              ws.send(JSON.stringify({
                error: 'Unknown action type',
                received: parsedMessage
              }));
          }
        } catch (error) {
          console.error(`Error handling message from ${email}:`, error);
          ws.send(JSON.stringify({
            error: `Failed to process message: ${error.message}`
          }));
        }
      });

      ws.on('close', () => {
        console.log(`User with email ${email} disconnected`);
        leaveRoom(email);
        // Remove machine info if exists
        const machineId = clients[email]?.machineId;
        if (machineId && machineInfo[machineId]) {
          delete machineInfo[machineId];
        }
        delete clients[email];
        console.log('Current clients:', Object.keys(clients));
        console.log('Current rooms:', Object.keys(rooms));
      });

    } else {
      ws.close();
      console.log('Unauthorized connection attempt');
    }
  });

  // Log active connections every 30 seconds
  setInterval(() => {
    console.log('\nActive connections:');
    console.log('Clients:', Object.keys(clients));
    console.log('Rooms:', Object.keys(rooms).map(room => ({
      room,
      members: Array.from(rooms[room])
    })));
  }, 30000);
};

// Original sendCommandToAgent function - preserved exactly as is
const sendCommandToAgent = (userEmail, command) => {
  const clientSocket = clients[userEmail]?.ws;
  if (clientSocket && clientSocket.readyState === WebSocket.OPEN) {
    const message = JSON.stringify(command);
    clientSocket.send(message);
    console.log(`Command sent to user ${userEmail}:`, command);
    return true;
  } else {
    console.log(`No active connection found for user ${userEmail} or connection is not open`);
    return false;
  }
};

// Handler for machine registration
const handleMachineRegistration = (email, message, ws) => {
  const machineId = message.machine_id;
  const machineData = message.machine_data || {};

  if (machineId) {
    machineInfo[machineId] = {
      email: email,
      machineId: machineId,
      os: machineData.os || 'unknown',
      platform: machineData.platform || 'unknown',
      hostname: machineData.hostname || 'unknown',
      cpu_count: machineData.cpu_count || 0,
      memory_total: machineData.memory_total || 0,
      memory_available: machineData.memory_available || 0,
      capabilities: machineData.capabilities || [],
      registered_at: new Date().toISOString()
    };

    clients[email].machineId = machineId;

    console.log(`Machine registered: ${machineId} for user ${email}`);

    ws.send(JSON.stringify({
      action: 'machine_registered',
      machine_id: machineId,
      message: 'Machine successfully registered'
    }));

    // Notify room members if in a room
    const roomCode = clients[email]?.room;
    if (roomCode) {
      broadcastToRoom(roomCode, email, {
        action: 'machine_joined',
        machine_id: machineId,
        machine_data: machineInfo[machineId],
        user: email
      });
    }
  }
};

// Handler for listing machines in a room
const handleListMachines = (email, message, ws) => {
  const roomCode = clients[email]?.room;
  if (!roomCode) {
    ws.send(JSON.stringify({
      error: 'You must be in a room to list machines'
    }));
    return;
  }

  // Get all machines in the room
  const roomMachines = [];
  if (rooms[roomCode]) {
    rooms[roomCode].forEach((userEmail) => {
      const machineId = clients[userEmail]?.machineId;
      if (machineId && machineInfo[machineId]) {
        roomMachines.push(machineInfo[machineId]);
      }
    });
  }

  ws.send(JSON.stringify({
    action: 'machines_list',
    room_code: roomCode,
    machines: roomMachines
  }));
};

const handleNotebookExecution = (email, message) => {
  const roomCode = clients[email]?.room;
  if (!roomCode) {
    clients[email].ws.send(JSON.stringify({
      error: 'You must be in a room to execute notebook cells'
    }));
    return;
  }

  const targetMachines = message.target_machines || [];

  // If specific machines are targeted, send only to those
  if (targetMachines && targetMachines.length > 0) {
    targetMachines.forEach((machineId) => {
      if (machineInfo[machineId]) {
        const targetEmail = machineInfo[machineId].email;
        const clientSocket = clients[targetEmail]?.ws;
        if (clientSocket && clientSocket.readyState === WebSocket.OPEN) {
          clientSocket.send(JSON.stringify({
            action: 'notebook_execute',
            code: message.code,
            cell_id: message.cell_id,
            sender: email
          }));
        }
      }
    });
  } else {
    // Forward the execution request to all clients in the room
    broadcastToRoom(roomCode, email, {
      action: 'notebook_execute',
      code: message.code,
      cell_id: message.cell_id,
      sender: email
    });
  }
};

const handleNotebookResult = (email, message) => {
  const originalSender = message.original_sender;
  if (originalSender && clients[originalSender]) {
    // Send the execution result back to the original sender
    clients[originalSender].ws.send(JSON.stringify({
      action: 'notebook_result',
      result: message.result,
      cell_id: message.cell_id,
      code: message.code,
      executor: email
    }));

    console.log(`Notebook execution result sent back to ${originalSender} from ${email}`);
  }
};

// Handler functions for different message types
const handleJoinRoom = (email, message, ws) => {
  const roomCode = message.room_code;
  if (roomCode) {
    joinRoom(email, roomCode);
    console.log(`User ${email} joined room ${roomCode}`);

    // Notify all room members about the new participant
    broadcastToRoom(roomCode, email, {
      action: 'user_joined',
      message: `${email} has joined the room`,
      user: email
    });

    ws.send(JSON.stringify({
      action: 'room_joined',
      message: `Joined room ${roomCode}`,
      room_code: roomCode
    }));
  }
};

const handleBroadcast = (email, message) => {
  const roomCode = clients[email]?.room;
  console.log("message in broadcast", message);
  if (!roomCode) {
    clients[email].ws.send(JSON.stringify({
      error: 'You must be in a room to broadcast messages'
    }));
    return;
  }

  const targetMachines = message.target_machines || [];

  // If specific machines are targeted, send only to those
  if (targetMachines && targetMachines.length > 0) {
    console.log(`Broadcasting to specific machines: ${targetMachines.join(', ')}`);
    targetMachines.forEach((machineId) => {
      if (machineInfo[machineId]) {
        const targetEmail = machineInfo[machineId].email;
        const clientSocket = clients[targetEmail]?.ws;
        if (clientSocket && clientSocket.readyState === WebSocket.OPEN) {
          clientSocket.send(JSON.stringify({
            action: 'broadcast',
            message: message.command,
            sender: email,
            machine_id: machineId
          }));
        }
      }
    });
  } else {
    // Broadcast to all in the room
    broadcastToRoom(roomCode, email, {
      action: 'broadcast',
      message: message.command,
      sender: email
    });
  }
};

const handleNotification = (email, message) => {
  const roomCode = clients[email]?.room;
  if (!roomCode) {
    clients[email].ws.send(JSON.stringify({
      error: 'You must be in a room to send notifications'
    }));
    return;
  }

  broadcastToRoom(roomCode, email, {
    action: 'show_notification',
    message: message.message,
    type: message.type || 'info',
    sender: email
  });
};


const handlePythonOutput = (email, message) => {
  const originalSender = message.original_sender;
  if (originalSender && clients[originalSender]) {
    // Send the execution result back to the original sender
    clients[originalSender].ws.send(JSON.stringify({
      action: 'python_result',
      result: message.result,
      code: message.code,
      executor: email
    }));

    console.log(`Python execution result sent back to ${originalSender} from ${email}`);
  } else {
    console.log(`Original sender ${originalSender} not found for Python output`);
  }
};

const handlePythonExecution = (email, message) => {
  const roomCode = clients[email]?.room;
  if (!roomCode) {
    clients[email].ws.send(JSON.stringify({
      error: 'You must be in a room to execute Python code'
    }));
    return;
  }

  const targetMachines = message.target_machines || [];

  // If specific machines are targeted, send only to those
  if (targetMachines && targetMachines.length > 0) {
    console.log(`Executing Python code on specific machines: ${targetMachines.join(', ')}`);
    targetMachines.forEach((machineId) => {
      if (machineInfo[machineId]) {
        const targetEmail = machineInfo[machineId].email;
        const clientSocket = clients[targetEmail]?.ws;
        if (clientSocket && clientSocket.readyState === WebSocket.OPEN) {
          clientSocket.send(JSON.stringify({
            action: 'python_execute',
            code: message.code,
            sender: email,
            machine_id: machineId
          }));
          console.log(`Sent Python execution to machine ${machineId} (${targetEmail})`);
        }
      }
    });
  } else {
    // Broadcast to all machines in the room
    broadcastToRoom(roomCode, email, {
      action: 'python_execute',
      code: message.code,
      sender: email
    });
  }
};

const handleDirectMessage = (email, message) => {
  const targetEmail = message.target;
  const clientSocket = clients[targetEmail]?.ws;

  if (clientSocket && clientSocket.readyState === WebSocket.OPEN) {
    clientSocket.send(JSON.stringify({
      action: 'direct_message',
      message: message.message,
      sender: email
    }));
  } else {
    clients[email].ws.send(JSON.stringify({
      error: 'Target user not found or offline'
    }));
  }
};

const handleLeaveRoom = (email, message) => {
  leaveRoom(email);
  clients[email].ws.send(JSON.stringify({
    action: 'room_left',
    message: 'Successfully left the room'
  }));
};

// Enhanced broadcastToRoom function - maintained original functionality with added structured message support
const broadcastToRoom = (roomCode, senderEmail, command) => {
  const room = rooms[roomCode];
  if (room) {
    console.log(`Broadcasting to room ${roomCode} from ${senderEmail}:`, command);
    console.log('Room members:', Array.from(room));

    let broadcastCount = 0;
    room.forEach((email) => {
      if (email !== senderEmail) {
        const clientSocket = clients[email]?.ws;
        if (clientSocket && clientSocket.readyState === WebSocket.OPEN) {
          const message = JSON.stringify(command);
          clientSocket.send(message);
          console.log(`Message sent to ${email} in room ${roomCode}`);
          broadcastCount++;
        } else {
          console.log(`Client ${email} socket not available or not open`);
        }
      }
    });
    console.log(`Broadcast complete. Message sent to ${broadcastCount} users in room ${roomCode}`);
  } else {
    console.log(`No active room found with code: ${roomCode}`);
  }
};

// Helper functions
const joinRoom = (email, roomCode) => {
  leaveRoom(email);

  if (!rooms[roomCode]) {
    rooms[roomCode] = new Set();
  }

  rooms[roomCode].add(email);
  clients[email].room = roomCode;
  console.log(`Room ${roomCode} members:`, Array.from(rooms[roomCode]));
};

const leaveRoom = (email) => {
  const roomCode = clients[email]?.room;
  if (roomCode && rooms[roomCode]) {
    rooms[roomCode].delete(email);
    if (rooms[roomCode].size === 0) {
      delete rooms[roomCode];
      console.log(`Room ${roomCode} deleted - no more members`);
    } else {
      console.log(`User ${email} left room ${roomCode}. Remaining members:`, Array.from(rooms[roomCode]));
    }
    clients[email].room = null;
  }
};

module.exports = { setupWebSocket, sendCommandToAgent, broadcastToRoom };
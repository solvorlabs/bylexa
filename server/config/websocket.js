const WebSocket = require('ws');
const jwt = require('jsonwebtoken');

// Secret key used to decode the JWT token (should be the same as used in your client-side)
const JWT_SECRET = 'bylexa'; 

// Store connected clients by email
const clients = {};

// Store rooms and their participants
const rooms = {};

// Setup the WebSocket server
const setupWebSocket = (server) => {
  const wss = new WebSocket.Server({ server, path: '/ws' });

  wss.on('connection', (ws, req) => {
    const token = req.headers['authorization'].split(' ')[1]; // Extract Bearer token

    // Verify and decode the token to get the user's email
    let email;
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      email = decoded.email;
    } catch (error) {
      console.log('Invalid token. Closing connection.');
      ws.close();
      return;
    }

    // Associate the WebSocket connection with the user email
    if (email) {
      clients[email] = { ws, room: null };
      console.log(`User with email ${email} connected`);

      ws.on('message', async (message) => {
        try {
          const parsedMessage = JSON.parse(message.toString());
          console.log('Received message:', parsedMessage); // Debug log
          
          // Handle different actions based on the received message
          if (parsedMessage.action === 'join_room') {
            const roomCode = parsedMessage.room_code;
            if (roomCode) {
              // Assign the client to the specified room
              joinRoom(email, roomCode);
              console.log(`User ${email} joined room ${roomCode}`);
              console.log('Current room members:', rooms[roomCode]); // Debug log
              ws.send(JSON.stringify({ message: `Joined room ${roomCode}` }));
            }
          } else if (parsedMessage.action === 'broadcast') {
            const { room_code, command } = parsedMessage;
            console.log(`Broadcasting in room ${room_code} from ${email}:`, command); // Debug log
            
            // Check if user is in the room they're trying to broadcast to
            if (clients[email]?.room === room_code) {
              broadcastToRoom(room_code, email, command);
            } else {
              console.log(`User ${email} attempted to broadcast to room ${room_code} but is not a member`);
              ws.send(JSON.stringify({ 
                error: 'You must be in a room to broadcast messages' 
              }));
            }
          } else {
            console.log(`Received unhandled message type from ${email}:`, parsedMessage);
            // Echo back unhandled messages for debugging
            ws.send(JSON.stringify({ 
              message: 'Unhandled message type',
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
        delete clients[email];
        // Log current state after disconnect
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

// Helper function to join a room
const joinRoom = (email, roomCode) => {
  // Leave current room if any
  leaveRoom(email);
  
  // Ensure the room exists
  if (!rooms[roomCode]) {
    rooms[roomCode] = new Set();
  }

  // Add the client to the room
  rooms[roomCode].add(email);
  clients[email].room = roomCode;
  
  // Log room state after joining
  console.log(`Room ${roomCode} members:`, Array.from(rooms[roomCode]));
};

// Helper function to leave a room
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

// Function to broadcast a command to all clients in the room except the sender
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
          const message = JSON.stringify({ 
            sender: senderEmail, 
            command,
            room: roomCode 
          });
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

// Function to send a command directly to a specific user's Python module
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

module.exports = { setupWebSocket, sendCommandToAgent, broadcastToRoom };
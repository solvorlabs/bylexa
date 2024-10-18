const WebSocket = require('ws');

// Store connected clients (Python modules) by user email
const clients = {};

const setupWebSocket = (server) => {
  const wss = new WebSocket.Server({ server, path: '/ws' });

  wss.on('connection', (ws, req) => {
    const email = req.headers['authorization'];  // Change from token to email

    // Associate the WebSocket connection with the user email
    if (email) {
      clients[email] = ws;
      console.log(`User with email ${email} connected`);

      ws.on('message', (message) => {
        console.log(`Received message from client ${email}: ${message}`);
      });

      ws.on('close', () => {
        console.log(`User with email ${email} disconnected`);
        delete clients[email];
      });
    } else {
      ws.close();
      console.log('Unauthorized connection attempt');
    }
  });
};

// Function to send command to the user's Python module
const sendCommandToAgent = (userEmail, command) => {
  const clientSocket = clients[userEmail];
  if (clientSocket) {
    clientSocket.send(JSON.stringify(command));
    console.log(`Command sent to user ${userEmail}: ${JSON.stringify(command)}`);
  } else {
    console.log(`No active connection found for user ${userEmail}`);
  }
};

module.exports = { setupWebSocket, sendCommandToAgent };

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(bodyParser.json());
require('./db');

const genAI = new GoogleGenerativeAI(process.env.API_KEY_12607);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
const projectRoutes = require('./routes/projectRoutes');
const courseRoutes = require('./src/course-crafty/routes/courseRoutes');
const translationRoutes = require('./src/course-crafty/routes/translationRoutes');
const commandRoutes = require('./routes/commandRoutes');

let currentCommand = ""; // This will store the latest command sent via /send-command
app.get('/', (req, res) => {
  res.json("Hello there!! This is Bylexa(G.O.A.T. Greatest Of Automated Tasks) The Large Multi-Action Model")
})
app.get('/control', (req, res) => {
  // Send the current command to the ESP32
  if (currentCommand) {
    res.send(currentCommand); // Send the latest command to ESP32
  } else {
    res.status(400).send('No command available');
  }
});

app.post('/send-command', async (req, res) => {
  const { command } = req.body;
  console.log(`Received command: ${command}`);
  
  // Use Gemini to interpret and generate a response from the command
  const prompt = command;
  try {
    const result = await model.generateContent(prompt);
    const interpretedCommand = result.response.text();
    
    // Log the interpreted command and update the currentCommand
    console.log(`Interpreted command: ${interpretedCommand}`);
    if (prompt.includes("blink")) {
      currentCommand = "blink_led";
    } else if (prompt.includes("rotate")) {
      currentCommand = "rotate_servo";
    }
    console.log(currentCommand);
    res.json({ response });
  } catch (error) {
    console.error('Error generating content:', error);
    res.status(500).json({ error: 'Failed to process speech' });
  }
});

// Routes
app.use('/api/projects', projectRoutes);
app.use('/api/commands', commandRoutes);
app.use('/api/courses', courseRoutes);
app.use('/api/translations', translationRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

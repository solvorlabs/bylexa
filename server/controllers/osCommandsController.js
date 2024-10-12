const { GoogleGenerativeAI } = require('@google/generative-ai');
const { spawn } = require('child_process');
const genAI = new GoogleGenerativeAI(process.env.API_KEY_12607);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const interpretCommand = async (command) => {
  const prompt = `Interpret the following command: "${command}". Extract and return the application, action, and task in JSON format. For example: {"application": "browser", "action": "open", "task": "google.com"}`;

  try {
    const result = await model.generateContent(prompt);
    return JSON.parse(result.response.text().trim());
  } catch (error) {
    console.error('Error interpreting command:', error);
    throw new Error('Failed to interpret command');
  }
};

const executeOSCommand = async (interpretation) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['os_interaction.py', JSON.stringify(interpretation)]);
    
    let output = '';
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python script error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve(output.trim());
      } else {
        reject(new Error(`Python script exited with code ${code}`));
      }
    });
  });
};

exports.handleOSCommand = async (req, res) => {
  try {
    const { command } = req.body;
    const interpretation = await interpretCommand(command);
    const result = await executeOSCommand(interpretation);
    res.json({ success: true, result });
  } catch (error) {
    console.error('Error handling OS command:', error);
    res.status(500).json({ success: false, error: error.message });
  }
};
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { spawn } = require('child_process');
const { sendCommandToAgent } = require('../config/websocket');
const config = require('../config');
const genAI = new GoogleGenerativeAI(process.env.API_KEY_12607);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
const jwt = require('jsonwebtoken');

const interpretCommand = async (command) => {
  const prompt = `
You are an assistant that interprets user commands into structured JSON objects for execution.

**Instructions:**

- Read the following command: "${command}"
- Extract relevant information and represent it as a JSON object.
- Possible keys include:
  - **action**: The primary action to perform (e.g., "open", "run", "copy", "delete", "move", "schedule", "play", "pause", "stop", "close").
  - **application**: The application involved (e.g., "browser", "notepad", "media player").
  - **task**: Specific task or URL (e.g., "google.com", "write a letter").
  - **file_path**: Path to a file or directory.
  - **command_line**: Command-line instruction to execute.
  - **script_path**: Path to a script file.
  - **args**: List of arguments for scripts or commands.
  - **time**: Time for scheduling tasks (e.g., "5 PM", "2023-10-01 14:00").
  - **media_action**: Action related to media control (e.g., "play", "pause").
  - **media**: Media file or stream to play.
  - **clipboard_action**: Action for clipboard (e.g., "copy", "paste").
  - **text**: Text to copy to or paste from the clipboard.
  - **file_action**: File operation (e.g., "copy", "move", "delete", "create_directory").
  - **source**: Source path for file operations.
  - **destination**: Destination path for file operations.

- If a parameter is not applicable or not mentioned, you may omit it.
- **Do not include any explanations or extra text.**
- **Output the result as minified JSON only.**

**Examples:**

1. **Command**: "Open the browser and go to google.com"
   **Output**: {"action":"open","application":"browser","task":"google.com"}

2. **Command**: "Run the command ls -la"
   **Output**: {"action":"run","command_line":"ls -la"}

3. **Command**: "Copy the file from /user/docs to /backup/docs"
   **Output**: {"action":"file","file_action":"copy","source":"/user/docs","destination":"/backup/docs"}

4. **Command**: "Schedule a task to run backup.sh at 2 AM"
   **Output**: {"action":"schedule","task_command":{"action":"run","script_path":"backup.sh"},"time":"2 AM"}

5. **Command**: "Play the song song.mp3"
   **Output**: {"action":"media","media_action":"play","media":"song.mp3"}

Now, interpret the following command and provide the JSON output.
`;


  try {
    console.log(`Sending prompt to LLM: ${prompt}`);
    const result = await model.generateContent(prompt);
    let responseText = (await result.response.text()).trim();

    // Sanitize the response to ensure it's valid JSON
    responseText = responseText.replace(/```json/g, '').replace(/```/g, '').trim();

    // Validate JSON format
    if (!responseText.startsWith('{') && !responseText.startsWith('[')) {
      throw new Error('Response is not valid JSON');
    }

    const interpretedCommand = JSON.parse(responseText);
    console.log('Interpreted command:', interpretedCommand);

    // Check if required fields are present
    if (!interpretedCommand.action) {
      return { success: false, message: "Error: 'action' not specified in command." };
    }

    return { success: true, command: interpretedCommand };
  } catch (error) {
    console.error('Error interpreting command:', error);

    // Check if the error is a JSON parsing error and return a safe fallback
    if (error instanceof SyntaxError || error.message.includes('Unexpected token')) {
      console.log("Returning fallback message: Sorry, I didn’t get that. Please try again.");
      return { success: false, message: 'Sorry, I didn’t get that. Please try again.' };
    }

    // Return a generic failure message for other errors without throwing
    return { success: false, message: 'Failed to interpret the command.' };
  }
};

// Function to execute the OS command using Python script
const executeOSCommand = async (interpretation) => {
  return new Promise((resolve, reject) => {
    console.log('Executing OS command with interpretation:', interpretation); // Log interpretation
    const pythonProcess = spawn('python', ['scripts/os_interaction.py', JSON.stringify(interpretation)]);

    let output = '';
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`Python script output: ${data.toString()}`); // Log Python script output
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python script error: ${data}`); // Log any errors from the Python script
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        console.log('Python script finished successfully'); // Log successful completion
        resolve(output.trim());
      } else {
        console.error(`Python script exited with code ${code}`); // Log error code if script fails
        reject(new Error(`Python script exited with code ${code}`));
      }
    });
  });
};

// Controller to handle the OS command
exports.handleOSCommand = async (req, res) => {
  try {
    const { command } = req.body;
    console.log(`Received command: ${command}`); // Log received command

    // Interpret the command
    const interpretation = await interpretCommand(command);
    console.log('Interpretation result:', interpretation); // Log result of interpretation

    // If the interpretation has a message, return it to the client
    if (interpretation.message) {
      return res.status(200).json({ success: false, message: interpretation.message });
    }

    // Otherwise, execute the OS command
    const result = await executeOSCommand(interpretation);
    console.log('Final result after executing OS command:', result); // Log result of OS command execution

    // Respond back to the client
    res.status(200).json({ success: true, result });
  } catch (error) {
    console.error('Unexpected error handling OS command:', error.message); // Log any unexpected errors
    res.status(500).json({ success: false, message: 'An unexpected error occurred. Please try again.' });
  }
};

exports.handleModuleOsCommand = async (req, res) => {
  const { command } = req.body;
  const userToken = req.user.token;
  const decoded = jwt.verify(userToken, config.API_KEY_JWT);
  req.user = decoded;

  if (!command) {
    return res.status(400).json({ message: 'No command provided' });
  }

  try {
    // Interpret the command using Gemini
    const interpretedCommand = await interpretCommand(command);

    if (interpretedCommand.success === false) {
      return res.status(400).json({ message: interpretedCommand.message });
    }

    // Send the interpreted command to the user's Python module via WebSocket
    sendCommandToAgent(req.user.email, interpretedCommand);

    // Send response back to the frontend
    res.status(200).json({ message: 'Command sent successfully', command: interpretedCommand });
  } catch (error) {
    console.error('Error processing command:', error);
    res.status(500).json({ message: 'Failed to process command' });
  }
};
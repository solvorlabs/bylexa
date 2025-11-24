# Bylexa System Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Components](#architecture-components)
3. [Communication Flow](#communication-flow)
4. [Component Details](#component-details)
5. [Plugin System](#plugin-system)
6. [Script System](#script-system)
7. [Room System](#room-system)
8. [IoT Control System](#iot-control-system)
9. [Installation & Setup](#installation--setup)

---

## System Overview

**Bylexa (GOAT - Greatest Of Automated Tasks)** is a comprehensive multi-action automation platform that enables voice-controlled operation of:
- Operating systems (Windows, Linux)
- IoT devices and microcontrollers
- Web applications and services
- Remote computational resources

### Key Features
- Voice-to-command interpretation using Gemini AI
- WebSocket-based real-time communication
- Plugin and script management system
- Room-based collaborative computing
- IoT device control via HTTP endpoints
- Cross-platform OS automation

---

## Architecture Components

The Bylexa system consists of three main components:

### 1. Backend Server (Node.js)
- **Location**: `server/`
- **Technology**: Express.js + MongoDB + WebSocket
- **Port**: 3000 (HTTP), WebSocket at `/ws`
- **Purpose**: Central hub for command processing, user authentication, and real-time communication

### 2. Python OS Interaction Module
- **Location**: `os_interaction/`
- **Package Name**: `bylexa`
- **Installation**: `pip install bylexa`
- **Purpose**: Local OS control agent that executes commands on the user's machine

### 3. Web/Mobile Applications
- **Web User Interface**: `web-user/` (Vue.js)
- **Mobile App**: `mobile-app/` (React Native)
- **Purpose**: User interface for voice input and command control

---

## Communication Flow

```
┌─────────────────┐         WebSocket (JWT Auth)         ┌──────────────────┐
│   Web/Mobile    │◄──────────────────────────────────────►│  Backend Server  │
│   Application   │                                        │   (Node.js)      │
└─────────────────┘                                        └──────────────────┘
                                                                    │
                                                                    │
                                                           WebSocket (JWT Auth)
                                                                    │
                                                                    ▼
┌─────────────────┐                                        ┌──────────────────┐
│   Bylexa CLI    │                                        │  Python Module   │
│  (bylexa start) │◄───────────────────────────────────────│  (OS Control)    │
└─────────────────┘                                        └──────────────────┘
        │                                                           │
        │                                                           │
        ▼                                                           ▼
┌─────────────────┐                                        ┌──────────────────┐
│   OS Actions    │                                        │  Script Manager  │
│  (Automation)   │                                        │  (Custom Scripts)│
└─────────────────┘                                        └──────────────────┘
```

### Detailed Flow

1. **User Input Flow**:
   ```
   User speaks → Web/Mobile App → Voice to Text → Backend API
   → Gemini AI Parser → JSON Command → WebSocket → Python Module
   → OS Execution → Result → WebSocket → Backend → User
   ```

2. **IoT Control Flow**:
   ```
   User Command → Backend → Project/Command Model → Database
   → Microcontroller polls GET endpoint → Retrieves command → Executes
   ```

3. **Room System Flow**:
   ```
   User A joins room → Backend creates/joins room → User B joins same room
   → User A broadcasts command → Backend forwards to all room members
   → User B's Python module executes → Result sent back to User A
   ```

---

## Component Details

### Backend Server Components

#### 1. WebSocket Server (`server/config/websocket.js`)
- **Authentication**: JWT-based with secret key `bylexa`
- **Connection Management**: Maintains client connections by email
- **Room Management**: Creates and manages collaborative rooms

**Key Actions**:
- `join_room`: Join a collaborative room
- `leave_room`: Leave current room
- `broadcast`: Send message/command to all room members
- `python_execute`: Execute Python code on remote machines
- `python_output`: Return execution results
- `notebook_execute`: Execute Jupyter-like notebook cells
- `direct_message`: Send message to specific user

#### 2. Database Models

**User Model** (`server/models/User.js`):
```javascript
{
  name: String,
  email: String (unique),
  password: String (hashed with bcrypt),
  token: String (JWT)
}
```

**Project Model** (`server/models/Project.js`) - IoT Projects:
```javascript
{
  name: String,
  description: String,
  currentCommand: String,
  parameters: Array
}
```

**Command Model** (`server/models/Command.js`) - IoT Commands:
```javascript
{
  project: ObjectId,
  name: String,
  description: String,
  action: String,
  parameters: Array
}
```

**Script Model** (`server/models/Script.js`):
```javascript
{
  name: String,
  description: String,
  author: String,
  version: String,
  source: String (script code),
  requirements: Array,
  keywords: Array,
  rating: Number,
  downloads: Number,
  user_id: ObjectId
}
```

**Plugin Model** (`server/models/Plugin.js`):
```javascript
{
  name: String,
  description: String,
  author: String,
  version: String,
  plugin_file: Buffer (ZIP file),
  plugin_file_name: String,
  main_file: String,
  requirements: Array,
  keywords: Array,
  config: Object,
  enabled: Boolean,
  rating: Number,
  downloads: Number,
  user_id: ObjectId
}
```

#### 3. AI Command Interpretation (`server/controllers/osCommandsController.js`)

Uses **Gemini 1.5 Flash** model to parse natural language into structured JSON:

**Input Example**: "Run the backup script with verbose mode and target directory /data"

**Output Example**:
```json
{
  "action": "script",
  "script_name": "backup",
  "args": ["--verbose", "--target", "/data"]
}
```

**Supported Actions**:
- `open`: Open applications
- `run`: Run programs
- `script`: Execute custom scripts
- `copy`, `delete`, `move`: File operations
- `schedule`: Schedule tasks
- `media`: Media control (play, pause, volume, etc.)
- `close`: Close applications

#### 4. API Routes

**Authentication** (`/api/auth`):
- `POST /register`: Register new user
- `POST /login`: Login and get JWT token

**OS Commands** (`/api/os-commands`):
- `POST /handle`: Execute OS command via Python subprocess
- `POST /module`: Send command to connected Python module via WebSocket

**Projects** (`/api/projects`) - IoT System:
- `POST /`: Create new IoT project
- `GET /`: Get all projects
- `GET /:projectId`: Get specific project
- `PUT /:projectId`: Update project
- `DELETE /:projectId`: Delete project
- `POST /:projectId/parse-code`: Parse Arduino/C++ code to extract functions
- `POST /:projectId/execute`: Execute command with AI interpretation
- `GET /:projectId/current-command`: Get current command (polled by microcontroller)

**Scripts** (`/api/scripts`):
- `GET /registry`: Search scripts
- `GET /registry/:id`: Get script details
- `GET /registry/:id/download`: Download script
- `POST /registry`: Submit new script (auth required)
- `POST /registry/:id/rate`: Rate a script
- `GET /user`: Get user's scripts
- `PUT /registry/:id`: Update script
- `DELETE /registry/:id`: Delete script

**Plugins** (`/api/plugins`):
- `GET /registry`: Search plugins
- `GET /registry/:id`: Get plugin details
- `GET /registry/:id/download`: Download plugin (ZIP file)
- `POST /registry`: Upload new plugin (auth required, multipart form)
- `POST /registry/:id/rate`: Rate a plugin
- `POST /registry/:id/toggle`: Enable/disable plugin
- `GET /user`: Get user's plugins
- `PUT /registry/:id`: Update plugin
- `DELETE /registry/:id`: Delete plugin

### Python OS Interaction Module

#### 1. Main Components

**CLI Entry Point** (`bylexa/new_cli.py`):
```bash
# Available commands
bylexa login          # Authenticate and save token
bylexa start          # Start the Bylexa system
bylexa client         # Start WebSocket client
bylexa config         # Open configuration GUI
bylexa exec <cmd>     # Execute command directly
bylexa search <query> # Search community scripts
bylexa install <id>   # Install script from registry
bylexa validate <path> # Validate script file
bylexa publish <script> <metadata> # Publish script
bylexa parse <text>   # Parse natural language command
```

**WebSocket Client** (`bylexa/websocket_client.py`):
- Connects to backend WebSocket server
- Authenticates using stored JWT token
- Receives and executes commands from backend
- Sends execution results back to backend

**WebSocket Gateway** (`bylexa/websocket_gateway.py`):
- Alternative P2P WebSocket server
- Runs on `localhost:8765` by default
- Handles room management, event subscription, command execution

**Bylexa Orchestrator** (`bylexa/bylexa_orchestrator.py`):
- Main command processing engine
- Coordinates between AI parser, action executor, and script manager
- Manages system lifecycle

**AI Orchestrator** (`bylexa/ai_orchestrator.py`):
- Processes natural language commands
- Integrates with intent parser
- Coordinates command execution

**Intent Parser** (`bylexa/intent_parser.py`):
- Parses commands into structured intents
- Maintains command registry
- Handles parameter extraction

**Dialog Manager** (`bylexa/dialog_manager.py`):
- Manages conversation context
- Handles ambiguous commands
- Collects missing parameters
- Maintains conversation history

**Script Manager** (`bylexa/script_manager.py`):
- Manages custom user scripts
- Creates and maintains WebDriver sessions (for browser automation)
- Executes scripts with proper parameter passing
- Supports scripts with `create_instance`, `run`, or subprocess execution

**Actions Module** (`bylexa/actions.py`):
- Contains OS-level action implementations
- Handles file operations, app launching, media control, etc.

**Plugin System**:
- `plugin_dev_kit.py`: SDK for plugin development
- `plugin_validator.py`: Validates plugin structure and security
- `community_registry.py`: Manages plugin/script registry

**Configuration** (`bylexa/config.py`):
- Stores user settings
- Manages authentication tokens
- Handles script/plugin directories

**Config GUI** (`bylexa/config_gui.py`):
- Tkinter-based graphical interface
- Allows users to add/edit custom scripts
- Configure system settings
- Download and manage plugins

#### 2. Script Execution

Scripts can be defined in three ways:

**Method 1: Class-based with `create_instance`**:
```python
class MyScript:
    def execute(self, args, parameters):
        driver = parameters['driver']  # WebDriver instance
        # Your automation logic
        return "Success"

def create_instance():
    return MyScript()
```

**Method 2: Function-based with `run`**:
```python
def run(args, parameters):
    # Your logic here
    return "Success"
```

**Method 3: Standalone script**:
```python
# Script runs via subprocess
import sys
args = sys.argv[1:]
# Your logic
print("Success")
```

---

## Plugin System

### Architecture

Plugins are community-contributed extensions that add functionality to Bylexa.

### Plugin Structure (ZIP File)

```
plugin-name.zip
├── main.py              # Entry point
├── metadata.json        # Plugin metadata
├── requirements.txt     # Python dependencies
└── [other files]
```

### Plugin Metadata

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "author@example.com",
  "main_file": "main.py",
  "requirements": ["dependency1", "dependency2"],
  "keywords": ["automation", "browser"],
  "config": {
    "setting1": "default_value"
  }
}
```

### Plugin Development

1. Create plugin directory structure
2. Implement main.py with required interface
3. Create metadata.json
4. Test plugin locally using `bylexa validate`
5. Package as ZIP file
6. Upload via web interface or API

### Plugin Execution Flow

```
User Command → Backend detects plugin action → Checks if plugin enabled
→ Downloads plugin if not cached → Executes plugin main.py
→ Returns result to user
```

---

## Script System

### Purpose

Scripts are custom automation sequences created by users to extend Bylexa's capabilities.

### Script Categories

1. **Browser Automation**: Using Selenium WebDriver
2. **File Operations**: Custom file processing
3. **API Integration**: External service interactions
4. **System Administration**: Advanced OS operations

### Script Manager Features

- **WebDriver Session Management**: Maintains persistent browser sessions
- **Session Persistence**: Keeps browser open between script executions
- **Parameter Passing**: Supports dynamic parameters from voice commands
- **Error Handling**: Graceful error recovery and reporting

### Creating Custom Scripts

**Example: YouTube Search Script**

```python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class YouTubeSearch:
    def execute(self, args, parameters):
        driver = parameters['driver']
        query = args[0] if args else "default query"

        driver.get("https://www.youtube.com")
        search_box = driver.find_element("name", "search_query")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        return f"Searched for: {query}"

def create_instance():
    return YouTubeSearch()
```

**Usage**:
1. Save script in configured scripts directory
2. Add script configuration via `bylexa config`
3. Speak: "Search YouTube for holiday homework"
4. System executes script with "holiday homework" as parameter

---

## Room System

### Current Implementation

The room system enables multiple users to collaborate and share computational resources.

### Features

1. **Room Creation**: Automatically created when first user joins
2. **Room Joining**: Users join with room code
3. **Broadcasting**: Send commands to all room members
4. **Python Execution**: Execute Python code on remote machines
5. **Notebook-style Execution**: Jupyter-like cell execution

### Room WebSocket Actions

**Join Room**:
```javascript
{
  "action": "join_room",
  "room_code": "ABC123"
}
```

**Broadcast to Room**:
```javascript
{
  "action": "broadcast",
  "command": { /* command object */ },
  "message": "Hello room"
}
```

**Execute Python**:
```javascript
{
  "action": "python_execute",
  "code": "print('Hello from remote')",
  "sender": "user@example.com"
}
```

**Python Result**:
```javascript
{
  "action": "python_output",
  "result": { /* execution result */ },
  "code": "...",
  "original_sender": "user@example.com"
}
```

### Current Limitations & Improvements Needed

**Current**: Commands broadcast to ALL room members
**Needed**: Ability to select specific machines for execution

**Proposed Enhancement**:
```javascript
{
  "action": "python_execute",
  "code": "import platform; platform.machine()",
  "target_machines": ["machine-id-1", "machine-id-2"]  // NEW
}
```

**Implementation Plan**:
1. Add machine registration with unique IDs
2. Track machine capabilities (CPU, RAM, OS, etc.)
3. Add machine selection UI
4. Implement targeted command routing
5. Add load balancing for computational tasks

---

## IoT Control System

### Architecture

The IoT system uses a **polling-based** architecture where microcontrollers periodically check for new commands.

### Components

1. **Project**: Represents an IoT project/device
2. **Command**: Functions extracted from microcontroller code
3. **Current Command**: Latest command set for execution

### Workflow

1. **Setup Phase**:
   ```
   User creates project → Uploads Arduino/C++ code
   → Backend parses code to extract functions
   → Functions stored as Command objects
   ```

2. **Execution Phase**:
   ```
   User speaks command → AI interprets command
   → Matches to function name → Extracts parameters
   → Stores in Project.currentCommand
   ```

3. **Microcontroller Phase**:
   ```
   Microcontroller polls GET /api/projects/:id/current-command
   → Receives command and parameters
   → Executes corresponding function
   → (Optional) Reports back to backend
   ```

### Example

**Arduino Code**:
```cpp
void controlMotor(String action, int speed) {
  if (action == "forward") {
    // Move forward at speed
  }
}

void turnServo(int angle) {
  servo.write(angle);
}
```

**User Command**: "Move motor forward at speed 100"

**Parsed Command**:
```json
{
  "command": "controlMotor",
  "parameters": ["forward", "100"]
}
```

**Microcontroller Receives**:
```json
{
  "command": "controlMotor",
  "parameters": "forward, 100"
}
```

### Proposed Improvements

**Current Limitation**: Polling creates delay and uses bandwidth

**Enhancement Options**:
1. **WebSocket Connection**: Real-time push notifications
2. **MQTT Integration**: Standard IoT messaging protocol
3. **Device Registry**: Track online/offline status
4. **Command Queue**: Buffer multiple commands
5. **Bidirectional Communication**: Device reports status/sensor data

---

## Installation & Setup

### Backend Server

```bash
cd server
npm install
cp .env.example .env
# Edit .env with MongoDB URI and API keys
npm start
```

**Environment Variables**:
```
PORT=3000
MONGO_URI=mongodb://localhost:27017/bylexa
API_KEY_12607=<your-gemini-api-key>
JWT_SECRET=bylexa
```

### Python Module

```bash
cd os_interaction
pip install -e .
# OR
pip install bylexa
```

**First Time Setup**:
```bash
bylexa login       # Authenticate with backend
bylexa config      # Configure scripts and settings
bylexa start       # Start the Bylexa system
```

### Web Application

```bash
cd web-user
npm install
cp .env.example .env
# Edit .env with backend URL
npm run dev        # Development
npm run build      # Production build
```

### Mobile Application

```bash
cd mobile-app
npm install
# Configure backend URL in app config
npm start
```

---

## Security Considerations

1. **Authentication**: JWT-based with bcrypt password hashing
2. **Script Validation**: Sandbox execution for untrusted scripts
3. **Plugin Validation**: Security checks before execution
4. **WebSocket Auth**: Bearer token required for all connections
5. **File Upload**: Limited to 5MB, ZIP files only for plugins
6. **CORS**: Configured for specific origins

---

## Future Enhancements

1. **Machine Learning Models**: Train custom models for better intent recognition
2. **Multi-Language Support**: Support multiple spoken languages
3. **Advanced Room Features**: Machine selection, load balancing
4. **IoT WebSocket**: Real-time IoT device communication
5. **Plugin Marketplace**: Enhanced discovery and reviews
6. **Voice Feedback**: Text-to-speech responses
7. **Workflow Automation**: Chain multiple commands
8. **Context Awareness**: Remember previous commands
9. **Integration Hub**: Connect with popular services (IFTTT, Zapier, etc.)
10. **Mobile Offline Mode**: Execute cached commands without backend

---

## Troubleshooting

### Common Issues

**Issue**: Python module can't connect to backend
- Check WebSocket URL in config
- Verify JWT token is valid
- Ensure backend server is running

**Issue**: Scripts not executing
- Verify script path in config
- Check script has proper permissions
- Review script logs in bylexa config GUI

**Issue**: IoT device not receiving commands
- Check project ID is correct
- Verify network connectivity
- Ensure polling interval is appropriate

**Issue**: Plugin upload fails
- Verify file is valid ZIP
- Check file size (max 5MB)
- Ensure metadata.json is valid

---

## Development

### Running Tests

```bash
# Backend tests
cd server
npm test

# Python module tests
cd os_interaction
pytest

# Web application tests
cd web-user
npm run test
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

---

## License

MIT License - See LICENSE file for details

---

## Support

- GitHub Issues: https://github.com/exploring-solver/bylexa/issues
- Documentation: https://bylexa-user.netlify.app/
- Email: support@bylexa.com

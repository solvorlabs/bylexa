# Bylexa API Documentation

## Base URL

```
http://localhost:3000/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Table of Contents

1. [Authentication](#authentication-endpoints)
2. [OS Commands](#os-commands)
3. [Projects (IoT)](#projects-iot)
4. [Commands (IoT)](#commands-iot)
5. [Scripts](#scripts)
6. [Plugins](#plugins)
7. [WebSocket API](#websocket-api)

---

## Authentication Endpoints

### Register User

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "_id": "user_id",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Status Codes:**
- `201` - User created successfully
- `400` - Email already exists
- `500` - Server error

---

### Login

**POST** `/auth/login`

Login to existing account.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "_id": "user_id",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Status Codes:**
- `200` - Login successful
- `400` - Invalid credentials
- `500` - Server error

---

## OS Commands

### Execute OS Command (Direct)

**POST** `/os-commands/handle`

Execute an OS command directly via Python subprocess.

**Request Body:**
```json
{
  "command": "open chrome and go to youtube.com"
}
```

**Response:**
```json
{
  "success": true,
  "result": "Command executed successfully"
}
```

**Status Codes:**
- `200` - Command executed
- `400` - Invalid command
- `500` - Execution error

---

### Execute OS Command (Module)

**POST** `/os-commands/module`

Send command to connected Bylexa Python module via WebSocket.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "command": "open notepad"
}
```

**Response:**
```json
{
  "message": "Command sent successfully",
  "command": {
    "success": true,
    "command": {
      "action": "open",
      "application": "notepad"
    }
  }
}
```

**Status Codes:**
- `200` - Command sent to module
- `400` - No command provided or module not connected
- `500` - Processing error

---

## Projects (IoT)

### Create Project

**POST** `/projects`

Create a new IoT project.

**Request Body:**
```json
{
  "name": "Smart Home Controller",
  "description": "Control home automation devices"
}
```

**Response:**
```json
{
  "_id": "project_id",
  "name": "Smart Home Controller",
  "description": "Control home automation devices",
  "currentCommand": null,
  "parameters": []
}
```

**Status Codes:**
- `201` - Project created
- `500` - Server error

---

### Get All Projects

**GET** `/projects`

Retrieve all IoT projects.

**Response:**
```json
[
  {
    "_id": "project_id",
    "name": "Smart Home Controller",
    "description": "Control home automation devices",
    "currentCommand": "turnLightOn",
    "parameters": []
  }
]
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### Get Project

**GET** `/projects/:projectId`

Get a specific project by ID.

**Response:**
```json
{
  "_id": "project_id",
  "name": "Smart Home Controller",
  "description": "Control home automation devices",
  "currentCommand": "turnLightOn",
  "parameters": []
}
```

**Status Codes:**
- `200` - Success
- `404` - Project not found
- `500` - Server error

---

### Update Project

**PUT** `/projects/:projectId`

Update project details.

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "_id": "project_id",
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Status Codes:**
- `200` - Success
- `404` - Project not found
- `500` - Server error

---

### Delete Project

**DELETE** `/projects/:projectId`

Delete a project and all associated commands.

**Response:**
```json
{
  "message": "Project and associated commands deleted successfully"
}
```

**Status Codes:**
- `200` - Deleted successfully
- `404` - Project not found
- `500` - Server error

---

### Parse Arduino Code

**POST** `/projects/:projectId/parse-code`

Parse Arduino/C++ code to extract function signatures.

**Request Body:**
```json
{
  "code": "void turnLightOn() { }\nvoid setServo(int angle, int speed) { }"
}
```

**Response:**
```json
{
  "message": "Commands parsed and saved successfully",
  "commandsCount": 2
}
```

**Extracted Commands:**
- Function names become command names
- Parameters are extracted automatically

**Status Codes:**
- `200` - Success
- `500` - Parsing error

---

### Execute Command

**POST** `/projects/:projectId/execute`

Execute a natural language command on the project.

**Request Body:**
```json
{
  "command": "turn on the light"
}
```

**Process:**
1. AI interprets the command
2. Matches to available functions
3. Extracts parameters if needed
4. Sets as current command
5. Microcontroller polls for command

**Response:**
```json
{
  "status": "Command executed",
  "action": "turnLightOn",
  "parameters": []
}
```

**Status Codes:**
- `200` - Success
- `400` - Command not found or unable to interpret
- `404` - Project not found
- `500` - Server error

---

### Get Current Command

**GET** `/projects/:projectId/current-command`

Get the current command set for the project (polled by microcontroller).

**Response:**
```json
{
  "command": "turnLightOn",
  "parameters": []
}
```

**Usage:**
```cpp
// Arduino code
void loop() {
  // Poll every 5 seconds
  String cmd = httpGET("/api/projects/" + projectId + "/current-command");
  if (cmd == "turnLightOn") {
    turnLightOn();
  }
  delay(5000);
}
```

**Status Codes:**
- `200` - Command available
- `400` - No command available
- `404` - Project not found
- `500` - Server error

---

## Commands (IoT)

Commands are automatically created when parsing Arduino code. No manual endpoints for command management.

---

## Scripts

### Browse Scripts

**GET** `/scripts/registry`

Get all available scripts, with optional search.

**Query Parameters:**
- `q` (optional) - Search term

**Example:**
```
GET /scripts/registry?q=youtube
```

**Response:**
```json
{
  "scripts": [
    {
      "_id": "script_id",
      "name": "YouTube Searcher",
      "description": "Search YouTube using voice commands",
      "author": "user@example.com",
      "version": "1.0.0",
      "keywords": ["youtube", "search", "automation"],
      "rating": 4.5,
      "num_ratings": 10,
      "downloads": 150
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### Get Script Details

**GET** `/scripts/registry/:id`

Get detailed information about a script (excludes source code).

**Response:**
```json
{
  "_id": "script_id",
  "name": "YouTube Searcher",
  "description": "Search YouTube using voice commands",
  "author": "user@example.com",
  "version": "1.0.0",
  "keywords": ["youtube", "search", "automation"],
  "requirements": ["selenium", "webdriver-manager"],
  "rating": 4.5,
  "num_ratings": 10,
  "downloads": 150
}
```

**Status Codes:**
- `200` - Success
- `404` - Script not found
- `500` - Server error

---

### Download Script

**GET** `/scripts/registry/:id/download`

Download script source code (increments download count).

**Response:**
```json
{
  "name": "YouTube Searcher",
  "source": "from selenium import webdriver...",
  "requirements": ["selenium", "webdriver-manager"]
}
```

**Status Codes:**
- `200` - Success
- `404` - Script not found
- `500` - Server error

---

### View Script Source

**GET** `/scripts/registry/:id/source`

View script source code in browser.

**Response:**
HTML page with syntax-highlighted source code.

**Status Codes:**
- `200` - Success
- `404` - Script not found
- `500` - Server error

---

### View Script Documentation

**GET** `/scripts/registry/:id/docs`

View script documentation page.

**Response:**
HTML page with script metadata, requirements, and usage info.

**Status Codes:**
- `200` - Success
- `404` - Script not found
- `500` - Server error

---

### Submit Script

**POST** `/scripts/registry`

Submit a new script to the registry.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "YouTube Searcher",
  "description": "Search YouTube using voice commands",
  "version": "1.0.0",
  "source": "from selenium import webdriver...",
  "requirements": ["selenium", "webdriver-manager"],
  "keywords": ["youtube", "search", "automation"]
}
```

**Response:**
```json
{
  "_id": "script_id",
  "name": "YouTube Searcher",
  "author": "user@example.com",
  "version": "1.0.0",
  ...
}
```

**Status Codes:**
- `201` - Script created
- `500` - Server error

---

### Rate Script

**POST** `/scripts/registry/:id/rate`

Rate a script (1-5 stars).

**Authentication:** Required

**Request Body:**
```json
{
  "rating": 5
}
```

**Response:**
```json
{
  "rating": 4.7
}
```

**Status Codes:**
- `200` - Rating submitted
- `404` - Script not found
- `500` - Server error

---

### Get User's Scripts

**GET** `/scripts/user`

Get all scripts created by the authenticated user.

**Authentication:** Required

**Response:**
```json
{
  "scripts": [...]
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### Update Script

**PUT** `/scripts/registry/:id`

Update a script (only by author).

**Authentication:** Required

**Request Body:**
```json
{
  "description": "Updated description",
  "source": "updated code...",
  "version": "1.1.0"
}
```

**Response:**
```json
{
  "_id": "script_id",
  "name": "YouTube Searcher",
  "version": "1.1.0",
  ...
}
```

**Status Codes:**
- `200` - Success
- `404` - Script not found or unauthorized
- `500` - Server error

---

### Delete Script

**DELETE** `/scripts/registry/:id`

Delete a script (only by author).

**Authentication:** Required

**Response:**
```json
{
  "message": "Script deleted successfully"
}
```

**Status Codes:**
- `200` - Deleted successfully
- `404` - Script not found or unauthorized
- `500` - Server error

---

## Plugins

### Browse Plugins

**GET** `/plugins/registry`

Get all available plugins, with optional search.

**Query Parameters:**
- `q` (optional) - Search term

**Example:**
```
GET /plugins/registry?q=browser
```

**Response:**
```json
{
  "plugins": [
    {
      "_id": "plugin_id",
      "name": "Browser Automation",
      "description": "Advanced browser automation plugin",
      "author": "user@example.com",
      "version": "1.0.0",
      "main_file": "main.py",
      "keywords": ["browser", "automation", "selenium"],
      "rating": 4.8,
      "num_ratings": 25,
      "downloads": 300,
      "enabled": false
    }
  ]
}
```

**Note:** Plugin file content is not included in this response.

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### Get Plugin Details

**GET** `/plugins/registry/:id`

Get detailed information about a plugin (excludes file).

**Response:**
```json
{
  "_id": "plugin_id",
  "name": "Browser Automation",
  "description": "Advanced browser automation plugin",
  "author": "user@example.com",
  "version": "1.0.0",
  "main_file": "main.py",
  "requirements": ["selenium", "beautifulsoup4"],
  "keywords": ["browser", "automation"],
  "config": {
    "default_browser": "chrome",
    "headless": true
  },
  "rating": 4.8,
  "num_ratings": 25,
  "downloads": 300,
  "enabled": false
}
```

**Status Codes:**
- `200` - Success
- `404` - Plugin not found
- `500` - Server error

---

### Download Plugin

**GET** `/plugins/registry/:id/download`

Download plugin ZIP file (increments download count).

**Response:**
Binary ZIP file download

**Headers:**
```
Content-Type: application/zip
Content-Disposition: attachment; filename="plugin-name-1.0.0.zip"
```

**Status Codes:**
- `200` - Success
- `404` - Plugin not found or file missing
- `500` - Server error

---

### Upload Plugin

**POST** `/plugins/registry`

Upload a new plugin.

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `name` (string) - Plugin name
- `description` (string) - Plugin description
- `version` (string) - Version number
- `plugin_file` (file) - ZIP file containing plugin
- `main_file` (string) - Path to main file (e.g., "main.py")
- `requirements` (JSON array as string) - Python dependencies
- `keywords` (JSON array as string) - Keywords for search
- `config` (JSON object as string) - Configuration options

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('name', 'My Plugin');
formData.append('description', 'Description here');
formData.append('version', '1.0.0');
formData.append('plugin_file', fileInput.files[0]);
formData.append('main_file', 'main.py');
formData.append('requirements', JSON.stringify(['numpy', 'pandas']));
formData.append('keywords', JSON.stringify(['data', 'processing']));
formData.append('config', JSON.stringify({ option1: 'value1' }));

fetch('/api/plugins/registry', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});
```

**Response:**
```json
{
  "_id": "plugin_id",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "user@example.com",
  ...
}
```

**Validation:**
- File must be ZIP format
- Max size: 5MB
- Required fields: name, version, description, plugin_file, main_file

**Status Codes:**
- `201` - Plugin created
- `400` - Invalid file or missing fields
- `500` - Server error

---

### Rate Plugin

**POST** `/plugins/registry/:id/rate`

Rate a plugin (1-5 stars).

**Authentication:** Required

**Request Body:**
```json
{
  "rating": 5
}
```

**Response:**
```json
{
  "rating": 4.9
}
```

**Status Codes:**
- `200` - Rating submitted
- `404` - Plugin not found
- `500` - Server error

---

### Get User's Plugins

**GET** `/plugins/user`

Get all plugins created by the authenticated user.

**Authentication:** Required

**Response:**
```json
{
  "plugins": [...]
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### Update Plugin

**PUT** `/plugins/registry/:id`

Update a plugin (only by author).

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Form Fields:** (same as upload, all optional except version)

**Response:**
```json
{
  "_id": "plugin_id",
  ...
}
```

**Status Codes:**
- `200` - Success
- `404` - Plugin not found or unauthorized
- `500` - Server error

---

### Delete Plugin

**DELETE** `/plugins/registry/:id`

Delete a plugin (only by author).

**Authentication:** Required

**Response:**
```json
{
  "message": "Plugin deleted successfully"
}
```

**Status Codes:**
- `200` - Deleted successfully
- `404` - Plugin not found or unauthorized
- `500` - Server error

---

### Enable Plugin

**POST** `/plugins/registry/:id/enable`

Enable a plugin.

**Authentication:** Required

**Response:**
```json
{
  "enabled": true
}
```

**Status Codes:**
- `200` - Success
- `404` - Plugin not found
- `500` - Server error

---

### Disable Plugin

**POST** `/plugins/registry/:id/disable`

Disable a plugin.

**Authentication:** Required

**Response:**
```json
{
  "enabled": false
}
```

**Status Codes:**
- `200` - Success
- `404` - Plugin not found
- `500` - Server error

---

## WebSocket API

### Connection

**URL:** `ws://localhost:3000/ws`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

### Actions

See [ROOM_SYSTEM_GUIDE.md](./ROOM_SYSTEM_GUIDE.md) for complete WebSocket API documentation including:

- Machine registration
- Room management
- Python code execution
- Broadcast messages
- Notebook-style execution
- Machine listing

---

## Error Responses

All endpoints may return the following error formats:

### Validation Error

```json
{
  "error": "Validation failed",
  "details": {
    "email": "Email is required"
  }
}
```

### Authentication Error

```json
{
  "error": "Authentication required"
}
```

### Not Found Error

```json
{
  "error": "Resource not found"
}
```

### Server Error

```json
{
  "error": "Internal server error",
  "message": "Detailed error message"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting in production:

- Recommended: 100 requests per minute per IP
- Authentication endpoints: 10 requests per minute per IP

---

## CORS

CORS is enabled for all origins in development. Configure appropriate origins for production.

---

## API Versioning

Current version: v1 (implicit)

Future versions will use URL versioning:
```
http://localhost:3000/api/v2/...
```

---

## Pagination

Currently not implemented for list endpoints. All results are returned.

**Recommended for future:**
```
GET /scripts/registry?page=1&limit=20
```

---

## Best Practices

### 1. Authentication

Always include the JWT token in requests:

```javascript
fetch('/api/scripts/registry', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 2. Error Handling

Always check response status and handle errors:

```javascript
const response = await fetch('/api/scripts/registry');
if (!response.ok) {
  const error = await response.json();
  console.error('Error:', error.error);
  return;
}
const data = await response.json();
```

### 3. File Uploads

Use `FormData` for plugin uploads:

```javascript
const formData = new FormData();
formData.append('plugin_file', file);
// ... other fields
```

### 4. WebSocket Reconnection

Implement reconnection logic for WebSocket:

```javascript
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:3000/ws');

  ws.onclose = () => {
    setTimeout(connectWebSocket, 5000); // Reconnect after 5s
  };
}
```

---

## SDK / Client Libraries

### JavaScript/TypeScript

```javascript
import BylexaClient from 'bylexa-client';

const client = new BylexaClient({
  baseUrl: 'http://localhost:3000/api',
  token: 'your_jwt_token'
});

// Use the client
const scripts = await client.scripts.getAll();
```

### Python

```python
from bylexa import BylexaClient

client = BylexaClient(
    base_url='http://localhost:3000/api',
    token='your_jwt_token'
)

# Use the client
scripts = client.scripts.get_all()
```

---

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Authentication endpoints
- OS commands
- Projects (IoT)
- Scripts
- Plugins
- WebSocket support
- Machine registration and targeting

---

## Support

- GitHub Issues: https://github.com/exploring-solver/bylexa/issues
- Documentation: https://bylexa-user.netlify.app/
- Email: support@bylexa.com

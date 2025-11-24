# Bylexa Complete Setup and Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the System](#running-the-system)
5. [Development Setup](#development-setup)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, Linux (Ubuntu 20.04+), or macOS 10.15+
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Disk Space**: 2GB free space
- **Internet**: Stable internet connection

### Required Software

1. **Node.js** (v16 or higher)
   - Download: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

2. **Python** (3.8 or higher)
   - Download: https://www.python.org/downloads/
   - Verify: `python --version` or `python3 --version`

3. **MongoDB** (v5.0 or higher)
   - Download: https://www.mongodb.com/try/download/community
   - OR use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas

4. **Git**
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

### Optional (for development)

- **Postman** - API testing
- **MongoDB Compass** - Database GUI
- **VS Code** - Code editor with recommended extensions:
  - Python
  - ESLint
  - Prettier
  - GitLens

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/exploring-solver/bylexa.git
cd bylexa
```

### 2. Backend Server Setup

```bash
cd server
npm install
```

**Create environment file:**

```bash
cp .env.example .env
```

**Edit `.env` file:**

```bash
PORT=3000
MONGO_URI=mongodb://localhost:27017/bylexa
API_KEY_12607=your_gemini_api_key_here
JWT_SECRET=bylexa
NODE_ENV=development
```

**Get Gemini API Key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy and paste into `.env` file

### 3. Python Module Setup

```bash
cd ../os_interaction
pip install -e .
```

**Or install from PyPI (when published):**

```bash
pip install bylexa
```

**Verify installation:**

```bash
bylexa --help
```

### 4. Web Application Setup

```bash
cd ../web-user
npm install
```

**Create environment file:**

```bash
cp .env.example .env
```

**Edit `.env` file:**

```bash
VITE_BACKEND_URL=http://localhost:3000
```

### 5. Mobile Application Setup (Optional)

```bash
cd ../mobile-app
npm install
```

**Configure backend URL in app config.**

---

## Configuration

### MongoDB Setup

#### Option 1: Local MongoDB

1. **Install MongoDB:**
   - Follow installation guide for your OS

2. **Start MongoDB:**

**Windows:**
```bash
net start MongoDB
```

**Linux/macOS:**
```bash
sudo systemctl start mongod
# OR
mongod --dbpath /path/to/data/directory
```

3. **Verify MongoDB is running:**
```bash
mongosh
# You should see MongoDB shell
```

#### Option 2: MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster
3. Create database user
4. Whitelist your IP address
5. Get connection string
6. Update `MONGO_URI` in server `.env`:

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/bylexa?retryWrites=true&w=majority
```

### Bylexa Python Module Configuration

After installation, configure the module:

```bash
bylexa login
```

**Enter credentials:**
- Email: Your registered email
- Password: Your password

**This will:**
- Authenticate with the backend
- Store JWT token locally
- Configure default settings

**Open configuration GUI:**

```bash
bylexa config
```

**Configure:**
- Scripts directory
- Custom commands
- Default browser for automation
- Other preferences

---

## Running the System

### Development Mode

#### 1. Start MongoDB (if local)

**Windows:**
```bash
net start MongoDB
```

**Linux/macOS:**
```bash
sudo systemctl start mongod
```

#### 2. Start Backend Server

```bash
cd server
npm run dev
```

**Output:**
```
Server is running on port 3000
MongoDB connected successfully
```

#### 3. Start Web Application

**In a new terminal:**

```bash
cd web-user
npm run dev
```

**Output:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

**Open browser:** http://localhost:5173/

#### 4. Start Bylexa Python Module

**In a new terminal:**

```bash
bylexa start
```

**Output:**
```
Bylexa system started
Press Ctrl+C to stop
Connected to backend
Machine registered: YourComputer-123456
```

#### 5. (Optional) Start Mobile App

```bash
cd mobile-app
npm start
```

**Scan QR code with Expo Go app on your phone.**

### Production Mode

#### 1. Backend Server

```bash
cd server
npm start
```

**Or use PM2 for process management:**

```bash
npm install -g pm2
pm2 start index.js --name bylexa-server
pm2 save
pm2 startup
```

#### 2. Web Application

**Build for production:**

```bash
cd web-user
npm run build
```

**Serve with a static server:**

```bash
npm install -g serve
serve -s dist -l 5173
```

**Or deploy to:**
- Netlify: https://www.netlify.com/
- Vercel: https://vercel.com/
- GitHub Pages
- Any static hosting service

#### 3. Python Module

**Run as a service:**

**Linux (systemd):**

Create `/etc/systemd/system/bylexa.service`:

```ini
[Unit]
Description=Bylexa OS Control Module
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser
ExecStart=/usr/bin/bylexa start
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable bylexa
sudo systemctl start bylexa
```

**Windows (NSSM):**

1. Download NSSM: https://nssm.cc/download
2. Install service:

```bash
nssm install Bylexa "C:\Python39\Scripts\bylexa.exe" start
nssm start Bylexa
```

---

## Development Setup

### Running Tests

#### Backend Tests

```bash
cd server
npm test
```

#### Python Tests

```bash
cd os_interaction
pytest
```

#### Web Application Tests

```bash
cd web-user
npm run test
```

### Code Formatting

#### Backend (ESLint + Prettier)

```bash
cd server
npm run lint
npm run format
```

#### Python (Black + Flake8)

```bash
cd os_interaction
black .
flake8 .
```

### Database Seeding

**Create seed data for development:**

```bash
cd server
node scripts/seed.js
```

**This creates:**
- Sample user accounts
- Example projects
- Test scripts and plugins

---

## Production Deployment

### Environment Setup

1. **Set environment variables:**

```bash
# Backend
export NODE_ENV=production
export PORT=3000
export MONGO_URI=your_production_mongodb_uri
export API_KEY_12607=your_gemini_api_key
export JWT_SECRET=random_secure_string

# Web
export VITE_BACKEND_URL=https://your-backend-domain.com
```

2. **Security Configuration:**

**Backend (`server/index.js`):**

```javascript
// Update CORS for production
app.use(cors({
  origin: 'https://your-frontend-domain.com',
  credentials: true
}));

// Add security middleware
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

app.use(helmet());

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);
```

### Deployment Options

#### Option 1: Traditional VPS (DigitalOcean, AWS EC2, etc.)

1. **Provision server** (Ubuntu 20.04 recommended)

2. **Install dependencies:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org

# Install Python
sudo apt install -y python3.9 python3-pip

# Install Nginx
sudo apt install -y nginx
```

3. **Clone and setup:**

```bash
cd /var/www
sudo git clone https://github.com/exploring-solver/bylexa.git
cd bylexa
sudo chown -R $USER:$USER /var/www/bylexa
```

4. **Configure Nginx:**

Create `/etc/nginx/sites-available/bylexa`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Backend proxy
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket proxy
    location /ws {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    # Frontend
    location / {
        root /var/www/bylexa/web-user/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/bylexa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Setup SSL with Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

6. **Start services:**

```bash
cd /var/www/bylexa/server
pm2 start index.js --name bylexa-backend
pm2 save
pm2 startup
```

#### Option 2: Docker Deployment

**Create `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    restart: always
    volumes:
      - mongo-data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password

  backend:
    build: ./server
    restart: always
    ports:
      - "3000:3000"
    environment:
      MONGO_URI: mongodb://admin:password@mongodb:27017/bylexa?authSource=admin
      API_KEY_12607: ${API_KEY_12607}
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      - mongodb

  frontend:
    build: ./web-user
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mongo-data:
```

**Deploy:**

```bash
docker-compose up -d
```

#### Option 3: Serverless (Vercel/Netlify)

**Frontend on Netlify:**

1. Connect GitHub repository
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Set environment variables in Netlify dashboard

**Backend on Railway/Render:**

1. Connect GitHub repository
2. Select `server` directory
3. Set environment variables
4. Deploy

---

## Troubleshooting

### Common Issues

#### 1. Backend won't start

**Error: MongoDB connection failed**

**Solution:**
- Ensure MongoDB is running
- Check `MONGO_URI` in `.env`
- Verify network connectivity

```bash
# Test MongoDB connection
mongosh "your_connection_string"
```

**Error: Port 3000 already in use**

**Solution:**
```bash
# Find process using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/macOS

# Kill the process
kill -9 <PID>
```

#### 2. Python module won't install

**Error: Permission denied**

**Solution:**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install in virtual environment
pip install -e .
```

**Error: Missing dependencies**

**Solution:**
```bash
# Install build tools
# Windows: Install Visual Studio Build Tools
# Linux: sudo apt install python3-dev build-essential
# macOS: xcode-select --install

pip install --upgrade pip setuptools wheel
pip install -e .
```

#### 3. Web application won't start

**Error: Module not found**

**Solution:**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: Port 5173 in use**

**Solution:**
```bash
# Use different port
npm run dev -- --port 5174
```

#### 4. WebSocket connection fails

**Error: WebSocket connection refused**

**Solution:**
- Ensure backend server is running
- Check WebSocket URL in client
- Verify JWT token is valid
- Check firewall settings

```bash
# Test WebSocket connection
wscat -c ws://localhost:3000/ws -H "Authorization: Bearer YOUR_TOKEN"
```

#### 5. Commands not executing

**Error: Python module not receiving commands**

**Solution:**
- Verify WebSocket connection is established
- Check if machine is registered
- Ensure JWT token is valid and not expired
- Check server logs for errors

```bash
# Check connection status
bylexa status  # If implemented

# Re-login
bylexa login
```

### Logging

#### Enable Debug Logging

**Backend:**

```javascript
// server/index.js
const morgan = require('morgan');
app.use(morgan('dev'));
```

**Python:**

```python
# In your code
import logging
logging.basicConfig(level=logging.DEBUG)
```

**View Logs:**

```bash
# Backend (if using PM2)
pm2 logs bylexa-backend

# System logs
journalctl -u bylexa -f  # Linux systemd
```

### Performance Issues

#### High Memory Usage

**Solution:**
- Limit concurrent WebSocket connections
- Implement connection pooling
- Clear unused data periodically
- Optimize database queries

#### Slow Response Times

**Solution:**
- Enable database indexing
- Implement caching (Redis)
- Optimize API endpoints
- Use CDN for static files

---

## Maintenance

### Database Backup

**MongoDB:**

```bash
# Create backup
mongodump --uri="your_connection_string" --out=/path/to/backup

# Restore backup
mongorestore --uri="your_connection_string" /path/to/backup
```

**Automated backups (cron job):**

```bash
# Add to crontab
0 2 * * * /usr/bin/mongodump --uri="mongodb://localhost:27017/bylexa" --out=/backups/$(date +\%Y\%m\%d)
```

### Updates

**Backend:**

```bash
cd server
git pull
npm install
pm2 restart bylexa-backend
```

**Python Module:**

```bash
cd os_interaction
git pull
pip install -e . --upgrade
sudo systemctl restart bylexa
```

**Web Application:**

```bash
cd web-user
git pull
npm install
npm run build
```

### Monitoring

**Recommended Tools:**
- **PM2**: Process monitoring
- **MongoDB Atlas**: Database monitoring
- **New Relic/DataDog**: Application performance monitoring
- **Sentry**: Error tracking

---

## Security Best Practices

1. **Use strong JWT secrets**
2. **Enable HTTPS in production**
3. **Implement rate limiting**
4. **Validate all user inputs**
5. **Keep dependencies updated**
6. **Use environment variables for secrets**
7. **Implement proper CORS policies**
8. **Regular security audits**
9. **Monitor for suspicious activity**
10. **Backup data regularly**

---

## Support

- **Documentation**: https://bylexa-user.netlify.app/
- **Issues**: https://github.com/exploring-solver/bylexa/issues
- **Email**: support@bylexa.com
- **Community**: Discord/Slack (if available)

---

## License

MIT License - See LICENSE file for details

// main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const isDev = require('electron-is-dev');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

// Installation handlers
ipcMain.handle('install-ollama', async () => {
  return new Promise((resolve, reject) => {
    // For Windows, download and run Ollama installer
    const ollamaInstallCommand = 'powershell.exe -Command "' +
      'Invoke-WebRequest -Uri https://ollama.ai/download/windows -OutFile ollama-installer.exe;' +
      './ollama-installer.exe"';
    
    exec(ollamaInstallCommand, (error, stdout, stderr) => {
      if (error) {
        reject(`Ollama installation failed: ${error}`);
        return;
      }
      resolve('Ollama installed successfully');
    });
  });
});

ipcMain.handle('install-bylexa', async () => {
  return new Promise((resolve, reject) => {
    exec('pip install bylexa', (error, stdout, stderr) => {
      if (error) {
        reject(`Bylexa installation failed: ${error}`);
        return;
      }
      resolve('Bylexa installed successfully');
    });
  });
});

ipcMain.handle('start-bylexa', async () => {
  return new Promise((resolve, reject) => {
    exec('bylexa start', (error, stdout, stderr) => {
      if (error) {
        reject(`Bylexa start failed: ${error}`);
        return;
      }
      resolve('Bylexa started successfully');
    });
  });
});

ipcMain.handle('login-bylexa', async () => {
  return new Promise((resolve, reject) => {
    exec('bylexa login', (error, stdout, stderr) => {
      if (error) {
        reject(`Bylexa login failed: ${error}`);
        return;
      }
      resolve('Bylexa login successful');
    });
  });
});

// Handle app lifecycle
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('bylexaAPI', {
  runBylexaCommand: (command) => ipcRenderer.invoke('run-bylexa-command', command),
});

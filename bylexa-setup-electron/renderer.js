async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const output = await window.bylexaAPI.runBylexaCommand(`login ${email} ${password}`);
    document.getElementById('output').textContent = output;
  }
  
  async function startBylexa() {
    const output = await window.bylexaAPI.runBylexaCommand('start');
    document.getElementById('output').textContent = output;
  }
  
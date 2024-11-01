import React, { useState, useCallback } from 'react';
import { useAuth } from '../hooks/useAuth';
import WaveAnimation from './WaveAnimation';
import api from '../services/api';
import { invoke } from '@tauri-apps/api/core';

interface ShellSession {
  id: string;
  output: string[];
}

const VoiceAssistant: React.FC = () => {
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [listening, setListening] = useState(false);
  const [shellInput, setShellInput] = useState('');
  const [shellSessions, setShellSessions] = useState<ShellSession[]>([]);
  const { logout } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleVoiceCommand = () => {
    console.log("Initializing voice recognition...");
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.onstart = () => {
      setListening(true);
      console.log('Voice recognition started');
    };

    recognition.onresult = (event: any) => {
      const spokenCommand = event.results[0][0].transcript;
      setCommand(spokenCommand);
      setListening(false);
      console.log(`Voice command recognized: ${spokenCommand}`);
    };

    recognition.onerror = (event: any) => {
      setListening(false);
      console.error('Voice recognition error:', event.error);
    };

    recognition.start();
  };

  const handleBylexaCommand = async (type: string) => {
    console.log(`Sending Bylexa command of type: ${type}`);
    try {
      const result = await invoke('execute_command', { commandType: type });
      setResponse(result as string);
      console.log(`Bylexa ${type} command result:`, result);
    } catch (error) {
      console.error(`Error executing Bylexa ${type} command:`, error);
      setResponse(`Error: ${error}`);
    }
  };

  const startInteractiveShell = async () => {
    console.log("Starting interactive shell...");
    try {
      const sessionId = await invoke('start_interactive_shell');
      setShellSessions(prev => [
        ...prev,
        { id: sessionId as string, output: ['Interactive shell started.'] }
      ]);
      console.log(`Interactive shell started with session ID: ${sessionId}`);
    } catch (error) {
      console.error('Error starting interactive shell:', error);
      setResponse(`Error starting shell: ${error}`);
    }
  };

  const sendShellInput = async () => {
    if (!shellInput.trim()) return;
    console.log("Sending shell input:", shellInput);

    try {
      const lastSession = shellSessions[shellSessions.length - 1];
      const result = await invoke('send_shell_input', {
        sessionId: lastSession.id,
        input: shellInput
      });

      setShellSessions(prev => {
        const updatedSessions = [...prev];
        const lastSessionIndex = updatedSessions.length - 1;
        updatedSessions[lastSessionIndex] = {
          ...updatedSessions[lastSessionIndex],
          output: [...updatedSessions[lastSessionIndex].output, result as string]
        };
        return updatedSessions;
      });

      console.log(`Shell input response: ${result}`);
      setShellInput('');
    } catch (error) {
      console.error('Error sending shell input:', error);
      setResponse(`Error sending input: ${error}`);
    }
  };

  const sendVoiceCommand = async () => {
    if (!command) return;
    console.log("Sending voice command:", command);

    try {
      const result = await api.post(
        '/api/os-commands/module-execute',
        { command },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      setResponse(JSON.stringify(result.data, null, 2));
      console.log('Command sent successfully:', result.data);
    } catch (error) {
      console.error('Error sending command:', error);
      setResponse(`Error: ${error}`);
    }
  };

  const loginToBylexa = async () => {
    try {
      const result = await invoke('interactive_login', { email, password });
      console.log('Login result:', result);
      setResponse(result as string);
    } catch (error) {
      console.error('Login failed:', error);
      setResponse(`Login failed: ${error}`);
    }
  };


  const startBylexa = async () => {
    try {
      const result = await invoke('interactive_start');
      console.log('Start result:', result);
      setResponse(result as string);
    } catch (error) {
      console.error('Start failed:', error);
      setResponse(`Start failed: ${error}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-4xl font-bold mb-6 text-center text-cyan-300">Bylexa Assistant</h1>

      <div className="flex space-x-4 mb-4">
        <button
          onClick={() => handleBylexaCommand('login')}
          className="btn btn-primary"
        >
          Login to Bylexa
        </button>

        <button onClick={startBylexa} className="btn btn-secondary">
          Start Bylexa
        </button>
      </div>
      <div className="login-form">
        <h2>Login to Bylexa</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input input-bordered mb-2"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="input input-bordered mb-2"
        />
        <button onClick={loginToBylexa} className="btn btn-primary">
          Login
        </button>
      </div>

      <div className="flex space-x-4 mb-4">
        <button
          onClick={handleVoiceCommand}
          className="btn btn-primary"
          disabled={listening}
        >
          {listening ? 'Listening...' : 'Start Voice Command'}
        </button>

        <button
          onClick={startInteractiveShell}
          className="btn btn-secondary"
        >
          Start Interactive Shell
        </button>
      </div>

      {listening && <WaveAnimation />}

      <p className="text-xl mb-4 text-gray-400">
        Voice Command: <span className="text-cyan-300">{command}</span>
      </p>

      <div className="w-full max-w-lg mb-4 flex">
        <input
          type="text"
          value={shellInput}
          onChange={(e) => setShellInput(e.target.value)}
          placeholder="Enter shell command"
          className="input input-bordered flex-grow mr-2 bg-gray-800 text-white"
        />
        <button
          onClick={sendShellInput}
          className="btn btn-primary"
          disabled={shellSessions.length === 0}
        >
          Send
        </button>
      </div>

      <div className="flex space-x-4 mb-4">
        <button onClick={sendVoiceCommand} className="btn btn-secondary">
          Send Voice Command
        </button>

        <button onClick={logout} className="btn btn-error">
          Logout
        </button>
      </div>

      <div className="w-full max-w-lg bg-gray-800 p-6 rounded-lg shadow-lg text-left">
        <h2 className="text-2xl font-semibold text-cyan-300 mb-4">Response:</h2>
        <pre className="text-gray-300 whitespace-pre-wrap">{response}</pre>
      </div>

      {shellSessions.map((session, index) => (
        <div
          key={session.id}
          className="w-full max-w-lg bg-gray-800 p-6 rounded-lg shadow-lg text-left mt-4"
        >
          <h2 className="text-2xl font-semibold text-cyan-300 mb-4">
            Shell Session {index + 1}
          </h2>
          <pre className="text-gray-300 whitespace-pre-wrap">
            {session.output.join('\n')}
          </pre>
        </div>
      ))}
    </div>
  );
};

export default VoiceAssistant;

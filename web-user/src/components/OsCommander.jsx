import React, { useState } from "react";
import axios from "axios";
import Config from "../config/Config";

const OsCommander = () => {
  const [isListening, setIsListening] = useState(false);
  const [command, setCommand] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState(null);
  const [isShivamMode, setIsShivamMode] = useState(false);
  const [isAukaatMode, setIsAukaatMode] = useState(false);

  // Check if the browser supports the Web Speech API
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;

  const startListening = () => {
    if (!recognition) {
      setError("Speech Recognition API is not supported in your browser.");
      return;
    }

    setIsListening(true);
    recognition.start();

    recognition.onstart = () => {
      console.log("Listening...");
    };

    recognition.onspeechend = () => {
      setIsListening(false);
      recognition.stop();
    };

    recognition.onresult = (event) => {
      const spokenCommand = event.results[0][0].transcript;
      console.log("Command recognized:", spokenCommand);
      setCommand(spokenCommand);

      if (isShivamMode) {
        playAudio("shivam.mp3"); // Play Shivam Mode audio
      } else if (isAukaatMode) {
        playAudio("aukaat.mp3"); // Play Aukaat Mode audio
      } else {
        sendCommandToApi(spokenCommand); // If no modes are enabled, send command to API
      }
    };

    recognition.onerror = (event) => {
      setError("Error occurred in recognition: " + event.error);
      setIsListening(false);
    };
  };

  const stopListening = () => {
    setIsListening(false);
    if (recognition) {
      recognition.stop();
    }
  };

  // Function to send the voice command to the backend API
  const sendCommandToApi = async (spokenCommand) => {
    try {
      const response = await axios.post(`${Config.backendUrl}/api/os-commands/execute`, {
        command: spokenCommand,
      });
      console.log("Response from API:", response.data);
      setResponse(response.data.result); // Set response to show on screen
    } catch (err) {
      console.error("Error sending command to API:", err);
      setError("Failed to send command to the server.");
    }
  };

  // Function to play audio from public folder
  const playAudio = (fileName) => {
    const audio = new Audio(`/${fileName}`); // Make sure the audio file is in the public folder
    audio.play().catch((err) => {
      setError("Error playing audio: " + err.message);
    });
  };

  return (
    <div className="flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Voice Command Input</h1>
      
      {/* Shivam Mode and Aukaat Mode Toggles */}
      {/* <div className="flex space-x-4 mb-4">
        <button
          onClick={() => setIsShivamMode(!isShivamMode)}
          className={`px-6 py-2 font-semibold text-white rounded-lg 
            ${isShivamMode ? "bg-purple-500" : "bg-gray-500"} 
            hover:bg-purple-600 transition-all duration-300`}
        >
          {isShivamMode ? "Shivam Mode: ON" : "Enable Shivam Mode"}
        </button>
        <button
          onClick={() => setIsAukaatMode(!isAukaatMode)}
          className={`px-6 py-2 font-semibold text-white rounded-lg 
            ${isAukaatMode ? "bg-blue-500" : "bg-gray-500"} 
            hover:bg-blue-600 transition-all duration-300`}
        >
          {isAukaatMode ? "Aukaat Mode: ON" : "Enable Aukaat Mode"}
        </button>
      </div> */}

      <div className="flex space-x-4 mb-4">
        <button
          onClick={startListening}
          disabled={isListening}
          className={`px-6 py-2 font-semibold text-white rounded-lg 
            ${isListening ? "bg-gray-500" : "bg-green-500"} 
            hover:bg-green-600 transition-all duration-300`}
        >
          {isListening ? "Listening..." : "Start Listening"}
        </button>
        <button
          onClick={stopListening}
          disabled={!isListening}
          className={`px-6 py-2 font-semibold text-white rounded-lg 
            ${!isListening ? "bg-gray-500" : "bg-red-500"} 
            hover:bg-red-600 transition-all duration-300`}
        >
          Stop Listening
        </button>
      </div>

      {/* Display recognized command */}
      {command && (
        <p className="text-lg text-gray-700 mb-4">
          <span className="font-semibold">Command:</span> {command}
        </p>
      )}

      {/* Display API response */}
      {response && (
        <p className="text-lg text-blue-600 mb-4">
          <span className="font-semibold">Response from Server:</span> {response}
        </p>
      )}

      {/* Display error */}
      {error && (
        <p className="text-lg text-red-500 mb-4">
          <span className="font-semibold">Error:</span> {error}
        </p>
      )}
    </div>
  );
};

export default OsCommander;

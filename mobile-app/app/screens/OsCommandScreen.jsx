import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import Voice from 'react-native-voice';
import axios from 'axios';
import Config from '../../config/Config';

const OsCommandScreen = () => {
  const [isListening, setIsListening] = useState(false);
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initialize voice listener
    Voice.onSpeechResults = onSpeechResults;
    Voice.onSpeechError = onSpeechError;

    return () => {
      // Cleanup listeners on component unmount
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const startListening = async () => {
    setIsListening(true);
    setError(null);
    setCommand('');
    setResponse('');
    try {
      await Voice.start('en-US');
      console.log('Listening...');
    } catch (e) {
      console.error('Error starting speech recognition:', e);
      setError('Error starting speech recognition.');
      setIsListening(false);
    }
  };

  const stopListening = async () => {
    setIsListening(false);
    try {
      await Voice.stop();
      console.log('Stopped listening.');
    } catch (e) {
      console.error('Error stopping speech recognition:', e);
      setError('Error stopping speech recognition.');
    }
  };

  const onSpeechResults = (event) => {
    const spokenCommand = event.value[0];
    console.log('Recognized text:', spokenCommand);
    setCommand(spokenCommand);
    sendCommandToApi(spokenCommand);
  };

  const onSpeechError = (event) => {
    console.error('Speech recognition error:', event.error);
    setError('Speech recognition error: ' + event.error.message);
    setIsListening(false);
  };

  const sendCommandToApi = async (spokenCommand) => {
    try {
      console.log('Sending command to API:', spokenCommand);
      const response = await axios.post(`${Config.backendUrl}/api/os-commands/execute`, {
        command: spokenCommand,
      });
      console.log('Response from API:', response.data);
      if (response.data.success) {
        setResponse(response.data.result);
      } else {
        setResponse(response.data.message || 'Unknown error from server.');
      }
    } catch (err) {
      console.error('Error sending command to API:', err);
      setError('Failed to send command to the server.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Voice Command Input</Text>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          onPress={isListening ? stopListening : startListening}
          style={[styles.button, isListening ? styles.stopButton : styles.startButton]}
        >
          <Text style={styles.buttonText}>
            {isListening ? 'Stop Listening' : 'Start Listening'}
          </Text>
        </TouchableOpacity>
      </View>

      {command ? (
        <Text style={styles.responseText}>
          <Text style={styles.boldText}>Command:</Text> {command}
        </Text>
      ) : null}

      {response ? (
        <Text style={styles.responseText}>
          <Text style={styles.boldText}>Response from Server:</Text> {response}
        </Text>
      ) : null}

      {error ? (
        <Text style={styles.errorText}>
          <Text style={styles.boldText}>Error:</Text> {error}
        </Text>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 20,
  },
  button: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginHorizontal: 5,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  startButton: {
    backgroundColor: '#10B981',
  },
  stopButton: {
    backgroundColor: '#EF4444',
  },
  responseText: {
    fontSize: 16,
    marginBottom: 10,
    textAlign: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    marginBottom: 10,
    textAlign: 'center',
  },
  boldText: {
    fontWeight: 'bold',
  },
});

export default OsCommandScreen;

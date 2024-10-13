import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system'; // To handle file conversion or manipulation
import axios from 'axios';
import Config from '../../config/Config';

const OsCommandScreen = () => {
    const [isListening, setIsListening] = useState(false);
    const [command, setCommand] = useState('');
    const [response, setResponse] = useState('');
    const [error, setError] = useState(null);
    const [recording, setRecording] = useState(null);

    useEffect(() => {
        return () => {
            if (recording) {
                recording.stopAndUnloadAsync();
            }
        };
    }, [recording]);

    const startListening = async () => {
        try {
            await Audio.requestPermissionsAsync();
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });
            const { recording: recordingObject } = await Audio.Recording.createAsync(
                Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
            );
            setRecording(recordingObject);
            setIsListening(true);
            console.log('Listening...');
        } catch (err) {
            console.error('Failed to start recording', err);
            setError('Failed to start recording');
        }
    };

    const stopListening = async () => {
        if (!recording) {
            return;
        }
        setIsListening(false);
        try {
            await recording.stopAndUnloadAsync();
            const uri = recording.getURI();
            console.log('Recording stopped and stored at', uri);

            // Send the audio file to sarvam.ai for speech-to-text conversion
            const transcribedText = await convertSpeechToText(uri);

            if (transcribedText) {
                setCommand(transcribedText); // Set the transcribed command
                sendCommandToApi(transcribedText); // Send transcribed text to your backend
            }
        } catch (err) {
            console.error('Failed to stop recording', err);
            setError('Failed to stop recording');
        }
    };

    const convertSpeechToText = async (audioUri) => {
        try {
          // Check if the file exists and log its details
          const fileInfo = await FileSystem.getInfoAsync(audioUri);
          console.log('File info:', fileInfo);
      
          if (!fileInfo.exists) {
            throw new Error('File does not exist');
          }
      
          // Read the file content using expo-file-system
          const fileData = await FileSystem.readAsStringAsync(audioUri, {
            encoding: FileSystem.EncodingType.Base64, // Convert to Base64 encoding
          });
      
          const formData = new FormData();
          const audioFile = {
            uri: audioUri,
            name: 'audio.3gp', // Name the file as 3gp
            type: 'audio/3gp', // Set the file type to 3gp
          };
      
          // Append the file and other fields to formData
          formData.append('file', {
            uri: audioUri,
            name: 'audio.3gp',
            type: 'audio/3gp',
          });
          formData.append('prompt', 'Convert this speech to text');
      
          // Send the file to your backend
          const response = await axios.post(`${Config.backendUrl}/api/util/speech-to-text`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
          console.log(response);
          if (response.data && response.data.transcribedText) {
            console.log('Transcribed text:', response.data.transcribedText);
            return response.data.transcribedText;
          } else {
            setError('Failed to transcribe audio.');
            return null;
          }
        } catch (err) {
          if (err.response) {
            console.error('Error response data:', err.response.data);
            console.error('Error response status:', err.response.status);
          } else if (err.request) {
            console.error('Error request:', err.request);
          } else {
            console.error('Error message:', err.message);
          }
          setError('Error converting speech to text.');
          return null;
        }
      };
      

    const sendCommandToApi = async (spokenCommand) => {
        try {
            console.log('Sending transcribed command to API:', spokenCommand);
            const response = await axios.post(`${Config.backendUrl}/api/os-commands/execute`, {
                command: spokenCommand,
            });
            console.log('Response from API:', response.data);
            setResponse(response.data.result);
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

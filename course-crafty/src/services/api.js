import axios from 'axios';
import { API_URL } from '../Config';

// Create a new course
export const createCourse = async (courseData) => {
  try {
    const response = await axios.post(`${API_URL}/courses/create`, courseData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : new Error('Error creating course');
  }
};

// Generate lecture notes using AI
export const generateLecture = async (lectureData) => {
  try {
    const response = await axios.post(`${API_URL}/courses/generate-lecture`, lectureData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : new Error('Error generating lecture');
  }
};

// Translate course to another language
export const translateCourse = async (translationData) => {
  try {
    const response = await axios.post(`${API_URL}/translations/translate`, translationData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : new Error('Error translating course');
  }
};

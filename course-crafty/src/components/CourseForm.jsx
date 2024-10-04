import React, { useState } from 'react';
import { TextField, Button } from '@mui/material';
import axios from 'axios';

const CourseForm = ({ onCourseCreated }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/courses', { title, description, language });
      onCourseCreated();
    } catch (error) {
      console.error('Error creating course:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        label="Course Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        fullWidth
        required
      />
      <TextField
        label="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        fullWidth
        required
      />
      <TextField
        label="Language"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        fullWidth
        required
      />
      <Button type="submit" variant="contained" color="primary">
        Create Course
      </Button>
    </form>
  );
};

export default CourseForm;

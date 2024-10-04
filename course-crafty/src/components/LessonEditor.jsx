import React from 'react';
import { Button } from '@mui/material';
import axios from 'axios';

const LessonEditor = ({ course }) => {
  const generateContent = async () => {
    try {
      await axios.post(`/api/courses/${course._id}/generate`);
      // Refresh the course data
    } catch (error) {
      console.error('Error generating content:', error);
    }
  };

  return (
    <div>
      <Button variant="contained" onClick={generateContent}>
        Generate Course Content
      </Button>
      {/* Display lessons and their content */}
      {course.lessons.map((lesson, index) => (
        <div key={index}>
          <h3>{lesson.title}</h3>
          <p>{lesson.lectureNotes}</p>
          <p>{lesson.translatedContent}</p>
          {/* Display images and voiceovers */}
        </div>
      ))}
    </div>
  );
};

export default LessonEditor;

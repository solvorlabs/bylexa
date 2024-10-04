import React, { useState, useEffect } from 'react';
import { Container, Typography, Button } from '@mui/material';
import CourseList from './CourseList';
import CourseForm from './CourseForm';

const Dashboard = () => {
  const [courses, setCourses] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const fetchCourses = async () => {
    // Fetch courses from the backend
    // Set the courses state
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Course Creation Dashboard
      </Typography>
      <Button variant="contained" onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Hide Form' : 'Create New Course'}
      </Button>
      {showForm && <CourseForm onCourseCreated={fetchCourses} />}
      <CourseList courses={courses} />
    </Container>
  );
};

export default Dashboard;

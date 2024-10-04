import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import LessonEditor from '../components/LessonEditor';
import axios from 'axios';

const CoursePage = () => {
  const { id } = useParams();
  const [course, setCourse] = useState(null);

  const fetchCourse = async () => {
    try {
      const response = await axios.get(`/api/courses/${id}`);
      setCourse(response.data);
    } catch (error) {
      console.error('Error fetching course:', error);
    }
  };

  useEffect(() => {
    fetchCourse();
  }, [id]);

  if (!course) return <div>Loading...</div>;

  return (
    <div>
      <h2>{course.title}</h2>
      <LessonEditor course={course} />
    </div>
  );
};

export default CoursePage;

import React, { useState } from 'react';
import { createCourse } from '../services/api';

const CourseCreation = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('English');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleCreateCourse = async () => {
    setError(null);
    setSuccess(null);
    try {
      const courseData = { title, description, language };
      const result = await createCourse(courseData);
      setSuccess(`Course "${result.title}" created successfully!`);
    } catch (error) {
      setError('Failed to create course');
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Create Course</h2>
      <div className="mb-4">
        <input
          type="text"
          value={title}
          placeholder="Course Title"
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
        />
      </div>
      <div className="mb-4">
        <textarea
          value={description}
          placeholder="Course Description"
          onChange={(e) => setDescription(e.target.value)}
          className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
        />
      </div>
      <div className="mb-4">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
        >
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Spanish">Spanish</option>
          {/* Add more languages */}
        </select>
      </div>
      <button
        onClick={handleCreateCourse}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Create Course
      </button>

      {error && <p className="mt-4 text-red-500">{error}</p>}
      {success && <p className="mt-4 text-green-500">{success}</p>}
    </div>
  );
};

export default CourseCreation;

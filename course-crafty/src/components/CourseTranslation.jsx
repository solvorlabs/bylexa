import React, { useState } from 'react';
import { translateCourse } from '../services/api';

const CourseTranslation = ({ courseId }) => {
  const [targetLanguage, setTargetLanguage] = useState('Hindi');
  const [error, setError] = useState(null);
  const [translatedContent, setTranslatedContent] = useState(null);

  const handleTranslateCourse = async () => {
    setError(null);
    try {
      const translationData = { courseId, targetLanguage };
      const result = await translateCourse(translationData);
      setTranslatedContent(result.description);
    } catch (error) {
      setError('Failed to translate course');
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Translate Course</h2>
      <div className="mb-4">
        <select
          value={targetLanguage}
          onChange={(e) => setTargetLanguage(e.target.value)}
          className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
        >
          <option value="Hindi">Hindi</option>
          <option value="Spanish">Spanish</option>
          {/* Add more languages */}
        </select>
      </div>
      <button
        onClick={handleTranslateCourse}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Translate Course
      </button>

      {error && <p className="mt-4 text-red-500">{error}</p>}
      {translatedContent && (
        <p className="mt-4">
          <strong>Translated Course Description:</strong> {translatedContent}
        </p>
      )}
    </div>
  );
};

export default CourseTranslation;

import React, { useState } from 'react';
import { generateLecture } from '../services/api';

const LectureGeneration = ({ courseId }) => {
  const [lectureTitle, setLectureTitle] = useState('');
  const [lectureContent, setLectureContent] = useState('');
  const [generatedLecture, setGeneratedLecture] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerateLecture = async () => {
    setError(null);
    try {
      const lectureData = { courseId, lectureTitle, lectureContent };
      const result = await generateLecture(lectureData);
      setGeneratedLecture(result.lecture.content);
    } catch (error) {
      setError('Failed to generate lecture');
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Generate Lecture</h2>
      <div className="mb-4">
        <input
          type="text"
          value={lectureTitle}
          placeholder="Lecture Title"
          onChange={(e) => setLectureTitle(e.target.value)}
          className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
        />
      </div>
      <div className="mb-4">
        <textarea
          value={lectureContent}
          placeholder="Lecture Content"
          onChange={(e) => setLectureContent(e.target.value)}
          className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
        />
      </div>
      <button
        onClick={handleGenerateLecture}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Generate Lecture
      </button>

      {error && <p className="mt-4 text-red-500">{error}</p>}
      {generatedLecture && (
        <p className="mt-4">
          <strong>Generated Lecture:</strong> {generatedLecture}
        </p>
      )}
    </div>
  );
};

export default LectureGeneration;

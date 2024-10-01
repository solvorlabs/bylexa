import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import CourseCreation from './components/CourseCreation';
import LectureGeneration from './components/LectureGeneration';
import CourseTranslation from './components/CourseTranslation';

const App = () => {
  return (
    <Router>
      <div className="min-h-screen flex">
        {/* Sidebar */}
        <nav className="w-1/5 bg-gray-800 text-white flex flex-col">
          <div className="p-4 text-2xl font-bold border-b border-gray-700">Course Crafty Dashboard</div>
          <ul className="flex-grow p-4 space-y-4">
            <li>
              <Link to="/" className="block p-2 rounded hover:bg-gray-700">Create Course</Link>
            </li>
            <li>
              <Link to="/generate-lecture" className="block p-2 rounded hover:bg-gray-700">Generate Lecture</Link>
            </li>
            <li>
              <Link to="/translate-course" className="block p-2 rounded hover:bg-gray-700">Translate Course</Link>
            </li>
          </ul>
        </nav>

        {/* Main Content Area */}
        <div className="w-4/5 bg-gray-100 p-8">
          <Routes>
            <Route path="/" element={<CourseCreation />} />
            <Route path="/generate-lecture" element={<LectureGeneration courseId="603d8d1e8d1e1c23d8f9" />} />
            <Route path="/translate-course" element={<CourseTranslation courseId="603d8d1e8d1e1c23d8f9" />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;

import React from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import ProjectList from './components/ProjectList';
import ProjectDetail from './components/ProjectDetail';
import CreateProject from './components/CreateProject';
import DocumentationPage from './components/DocumentationPage';
import OsCommander from './components/OsCommander';
import AssistantInteraction from './components/AssistantInteraction';
import VoiceCommandSender from './components/VoiceCommandSender';
import PrivateRoute from './auth/PrivateRoute';
import Register from './auth/Register';
import Login from './auth/Login';

const App = () => {
  return (
    <Router>
      <div className=" px-10 p-4 bg-gray-900">
        <nav className="mb-4">
          <ul className="flex justify-between flex-wrap ">
            <li><Link to="/" className="text-blue-500 underline hover:text-blue-700">Projects</Link></li>
            <li><Link to="/create" className="text-blue-500 underline hover:text-blue-700">Create Project</Link></li>
            <li><Link to="/module-command" className="text-blue-500 underline hover:text-blue-700">Python Client Commander</Link></li>
            <li><Link to="/os-command" className="text-blue-500 underline hover:text-blue-700">OS Commander</Link></li>
            <li><Link to="/assistant" className="text-blue-500 underline hover:text-blue-700">Assistant</Link></li>
            <li><Link to="/documentation" className="text-blue-500 underline hover:text-blue-700">Documentation/Guide</Link></li>
          </ul>
        </nav>
      </div>
      <Routes>
        <Route path="/" element={<ProjectList/>} />
        <Route path="/login" element={<Login/>} />
        <Route path="/register" element={<Register/>} />
        <Route path="/project/:id" element={<ProjectDetail/>} />
        <Route path="/create" element={<CreateProject/>} />
        <Route path="/os-command" element={<OsCommander/>} />
        <Route path="/module-command" element={<PrivateRoute><VoiceCommandSender/></PrivateRoute>} />
        <Route path="/assistant" element={<AssistantInteraction/>} />
        <Route path="/documentation" element={<DocumentationPage/>} />
      </Routes>
    </Router>
  );
};

export default App;
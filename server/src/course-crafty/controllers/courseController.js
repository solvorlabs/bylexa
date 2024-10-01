const Course = require('../models/courseModel');
const aiService = require('../services/aiService');

exports.createCourse = async (req, res) => {
  try {
    const { title, description, language } = req.body;
    const course = new Course({ title, description, language });
    await course.save();
    res.status(201).json(course);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create course' });
  }
};

exports.generateLecture = async (req, res) => {
  try {
    const { courseId, lectureTitle, lectureContent } = req.body;
    
    const course = await Course.findById(courseId);
    if (!course) return res.status(404).json({ error: 'Course not found' });

    // AI-enhanced content generation (using Gemini)
    const prompt = `Generate lecture notes based on the content: "${lectureContent}".`;
    const generatedLectureNotes = await aiService.generateContent(prompt);

    const lecture = { title: lectureTitle, content: generatedLectureNotes, course: courseId };
    course.lectures.push(lecture);
    await course.save();
    res.status(201).json({ lecture });
  } catch (error) {
    res.status(500).json({ error: 'Failed to generate lecture' });
  }
};

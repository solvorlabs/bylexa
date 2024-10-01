const mongoose = require('mongoose');

const courseSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String },
  language: { type: String, default: 'English' },
  lectures: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Lecture' }],
  createdAt: { type: Date, default: Date.now }
});

const Course = mongoose.model('Course', courseSchema);
module.exports = Course;

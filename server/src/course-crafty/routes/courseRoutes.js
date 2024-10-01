const express = require('express');
const { createCourse, generateLecture } = require('../controllers/courseController');
const router = express.Router();

router.post('/create', createCourse);
router.post('/generate-lecture', generateLecture);

module.exports = router;

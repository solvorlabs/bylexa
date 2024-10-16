const express = require('express');
const { register, login, authMiddleware } = require('../controllers/authControllers');

const router = express.Router();

// Public routes
router.post('/register', register);
router.post('/login', login);

// Example of a protected route
router.get('/protected', authMiddleware, (req, res) => {
  res.json({ message: `Welcome, ${req.user.username}` });
});

module.exports = router;

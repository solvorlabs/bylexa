const express = require('express');
const router = express.Router();
const osCommandsController = require('../controllers/osCommandsController');

router.post('/execute', osCommandsController.handleOSCommand);

module.exports = router;
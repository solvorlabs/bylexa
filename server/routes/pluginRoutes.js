const express = require('express');
const router = express.Router();
const Plugin = require('../models/Plugin');
const multer = require('multer');
const { authMiddleware } = require('../controllers/authControllers');
const fs = require('fs');

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'uploads/plugins';
        // Create directory if it doesn't exist
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + '-' + file.originalname);
    }
});

const upload = multer({ 
    storage: storage,
    fileFilter: function (req, file, cb) {
        // Accept only .py files or other specific extensions you want to allow
        if (!file.originalname.match(/\.(py|js|json)$/)) {
            return cb(new Error('Only .py, .js, and .json files are allowed!'), false);
        }
        cb(null, true);
    }
});

// Get all plugins with optional search
router.get('/registry', async (req, res) => {
    try {
        const searchQuery = req.query.q;
        let query = {};
        
        if (searchQuery) {
            query = {
                $or: [
                    { name: { $regex: searchQuery, $options: 'i' } },
                    { description: { $regex: searchQuery, $options: 'i' } },
                    { keywords: { $regex: searchQuery, $options: 'i' } }
                ]
            };
        }

        const plugins = await Plugin.find(query).select('-main_file');
        res.json({ plugins });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get plugin details
router.get('/registry/:id', async (req, res) => {
    try {
        const plugin = await Plugin.findById(req.params.id).select('-main_file');
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found' });
        }
        res.json(plugin);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Download plugin
router.get('/registry/:id/download', async (req, res) => {
    try {
        const plugin = await Plugin.findById(req.params.id);
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found' });
        }

        // Increment download count
        plugin.downloads += 1;
        await plugin.save();

        res.json({
            name: plugin.name,
            main_file: plugin.main_file,
            config: plugin.config,
            requirements: plugin.requirements
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Submit new plugin (requires authentication)
router.post('/registry', authMiddleware, upload.single('plugin_file'), async (req, res) => {
    try {
        const pluginData = {
            ...req.body,
            user_id: req.user._id,
            author: req.user.email
        };

        // Parse arrays that come as strings
        if (typeof req.body.requirements === 'string') {
            pluginData.requirements = JSON.parse(req.body.requirements);
        }
        if (typeof req.body.keywords === 'string') {
            pluginData.keywords = JSON.parse(req.body.keywords);
        }

        if (req.file) {
            pluginData.main_file = req.file.path;
        }

        const plugin = new Plugin(pluginData);
        await plugin.save();
        res.status(201).json(plugin);
    } catch (error) {
        // Clean up uploaded file if there's an error
        if (req.file) {
            fs.unlink(req.file.path, (err) => {
                if (err) console.error('Error deleting file:', err);
            });
        }
        res.status(500).json({ error: error.message });
    }
});

// Rate a plugin
router.post('/registry/:id/rate', authMiddleware, async (req, res) => {
    try {
        const { rating } = req.body;
        const plugin = await Plugin.findById(req.params.id);
        
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found' });
        }

        // Update rating
        const newRating = (plugin.rating * plugin.num_ratings + rating) / (plugin.num_ratings + 1);
        plugin.rating = newRating;
        plugin.num_ratings += 1;
        await plugin.save();

        res.json({ rating: plugin.rating });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get user's plugins
router.get('/user', authMiddleware, async (req, res) => {
    try {
        const plugins = await Plugin.find({ user_id: req.user._id });
        res.json({ plugins });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update plugin
router.put('/registry/:id', authMiddleware, upload.single('plugin_file'), async (req, res) => {
    try {
        const plugin = await Plugin.findOne({ 
            _id: req.params.id, 
            user_id: req.user._id 
        });
        
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found or unauthorized' });
        }

        const updateData = { ...req.body };

        // Parse arrays that come as strings
        if (typeof req.body.requirements === 'string') {
            updateData.requirements = JSON.parse(req.body.requirements);
        }
        if (typeof req.body.keywords === 'string') {
            updateData.keywords = JSON.parse(req.body.keywords);
        }

        if (req.file) {
            // Delete old file if it exists
            if (plugin.main_file) {
                fs.unlink(plugin.main_file, (err) => {
                    if (err) console.error('Error deleting old file:', err);
                });
            }
            updateData.main_file = req.file.path;
        }

        Object.assign(plugin, updateData);
        plugin.updated_at = Date.now();
        await plugin.save();
        
        res.json(plugin);
    } catch (error) {
        // Clean up uploaded file if there's an error
        if (req.file) {
            fs.unlink(req.file.path, (err) => {
                if (err) console.error('Error deleting file:', err);
            });
        }
        res.status(500).json({ error: error.message });
    }
});

// Delete plugin
router.delete('/registry/:id', authMiddleware, async (req, res) => {
    try {
        const plugin = await Plugin.findOneAndDelete({ 
            _id: req.params.id, 
            user_id: req.user._id 
        });
        
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found or unauthorized' });
        }
        
        // Clean up plugin file
        if (plugin.main_file) {
            fs.unlink(plugin.main_file, (err) => {
                if (err) console.error('Error deleting plugin file:', err);
            });
        }
        
        res.json({ message: 'Plugin deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Toggle plugin status
router.post('/registry/:id/toggle', authMiddleware, async (req, res) => {
    try {
        const { enabled } = req.body;
        const plugin = await Plugin.findById(req.params.id);
        
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found' });
        }

        plugin.enabled = enabled;
        await plugin.save();

        res.json({ enabled: plugin.enabled });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 
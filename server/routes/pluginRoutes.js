const express = require('express');
const router = express.Router();
const Plugin = require('../models/Plugin');
const multer = require('multer');
const { authMiddleware } = require('../controllers/authControllers');
const fs = require('fs');
const path = require('path');

// Configure multer for memory storage
const storage = multer.memoryStorage();
const upload = multer({ 
    storage: storage,
    fileFilter: (req, file, cb) => {
        // Accept common zip MIME types and check file extension
        const allowedMimeTypes = [
            'application/zip',
            'application/x-zip-compressed',
            'application/octet-stream'
        ];
        
        const isZipMime = allowedMimeTypes.includes(file.mimetype);
        const isZipExtension = file.originalname.toLowerCase().endsWith('.zip');

        if (isZipMime || isZipExtension) {
            cb(null, true);
        } else {
            cb(new Error(`Invalid file type. Expected .zip file, got ${file.mimetype}`));
        }
    },
    limits: {
        fileSize: 5 * 1024 * 1024 // 5MB limit
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
                    { keywords: { $in: [new RegExp(searchQuery, 'i')] } }
                ]
            };
        }

        const plugins = await Plugin.find(query).select('-plugin_file');
        res.json({ plugins });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get plugin details
router.get('/registry/:id', async (req, res) => {
    try {
        const plugin = await Plugin.findById(req.params.id).select('-plugin_file');
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
        if (!plugin || !plugin.plugin_file) {
            return res.status(404).json({ error: 'Plugin not found or plugin file missing' });
        }

        // Increment download count
        plugin.downloads += 1;
        await plugin.save();

        // Set headers for zip file download
        res.set({
            'Content-Type': 'application/zip',
            'Content-Disposition': `attachment; filename="${plugin.name}-${plugin.version}.zip"`,
            'Content-Length': plugin.plugin_file.length
        });

        // Send the zip file
        res.send(plugin.plugin_file);
    } catch (error) {
        console.error('Error downloading plugin:', error);
        res.status(500).json({ error: error.message });
    }
});

// Submit new plugin (requires authentication)
router.post('/registry', authMiddleware, upload.single('plugin_file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'Plugin file is required' });
        }

        const pluginData = {
            ...req.body,
            plugin_file: req.file.buffer,
            plugin_file_name: req.file.originalname,
            author: req.user.email,
            main_file: req.body.main_file || 'main.py'  // Add default if not provided
        };

        // Parse arrays that come as strings
        if (typeof req.body.requirements === 'string') {
            pluginData.requirements = JSON.parse(req.body.requirements);
        }
        if (typeof req.body.keywords === 'string') {
            pluginData.keywords = JSON.parse(req.body.keywords);
        }
        if (typeof req.body.config === 'string') {
            pluginData.config = JSON.parse(req.body.config);
        }

        const plugin = new Plugin(pluginData);
        await plugin.save();

        // Send response without the plugin file
        const response = plugin.toObject();
        delete response.plugin_file;
        res.status(201).json(response);
    } catch (error) {
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
        const plugin = await Plugin.findById(req.params.id);
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found' });
        }

        const updateData = { ...req.body };

        // Update file if provided
        if (req.file) {
            updateData.plugin_file = req.file.buffer;
            updateData.plugin_file_name = req.file.originalname;
        }

        // Parse JSON strings
        ['requirements', 'keywords', 'config'].forEach(field => {
            if (typeof req.body[field] === 'string') {
                updateData[field] = JSON.parse(req.body[field]);
            }
        });

        Object.assign(plugin, updateData);
        await plugin.save();

        // Send response without the plugin file
        const response = plugin.toObject();
        delete response.plugin_file;
        res.json(response);
    } catch (error) {
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

// Enable plugin
router.post('/registry/:id/enable', authMiddleware, async (req, res) => {
    try {
        const plugin = await Plugin.findById(req.params.id);
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found' });
        }
        plugin.enabled = true;
        await plugin.save();
        res.json({ enabled: plugin.enabled });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Disable plugin
router.post('/registry/:id/disable', authMiddleware, async (req, res) => {
    try {
        const plugin = await Plugin.findById(req.params.id);
        if (!plugin) {
            return res.status(404).json({ error: 'Plugin not found' });
        }
        plugin.enabled = false;
        await plugin.save();
        res.json({ enabled: plugin.enabled });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
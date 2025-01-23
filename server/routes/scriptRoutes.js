const express = require('express');
const router = express.Router();
const Script = require('../models/Script');
const { authMiddleware } = require('../controllers/authControllers');

// Get all scripts with optional search
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

        const scripts = await Script.find(query).select('-source');
        res.json({ scripts });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get script details
router.get('/registry/:id', async (req, res) => {
    try {
        const script = await Script.findById(req.params.id).select('-source');
        if (!script) {
            return res.status(404).json({ error: 'Script not found' });
        }
        res.json(script);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Download script
router.get('/registry/:id/download', async (req, res) => {
    try {
        const script = await Script.findById(req.params.id);
        if (!script) {
            return res.status(404).json({ error: 'Script not found' });
        }

        // Increment download count
        script.downloads += 1;
        await script.save();

        res.json({
            name: script.name,
            source: script.source,
            requirements: script.requirements
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Submit new script (requires authentication)
router.post('/registry', authMiddleware, async (req, res) => {
    try {
        const script = new Script({
            ...req.body,
            user_id: req.user._id,
            author: req.user.email
        });
        await script.save();
        res.status(201).json(script);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Rate a script
router.post('/registry/:id/rate', authMiddleware, async (req, res) => {
    try {
        const { rating } = req.body;
        const script = await Script.findById(req.params.id);
        
        if (!script) {
            return res.status(404).json({ error: 'Script not found' });
        }

        // Update rating
        const newRating = (script.rating * script.num_ratings + rating) / (script.num_ratings + 1);
        script.rating = newRating;
        script.num_ratings += 1;
        await script.save();

        res.json({ rating: script.rating });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get user's scripts
router.get('/user', authMiddleware, async (req, res) => {
    try {
        const scripts = await Script.find({ user_id: req.user._id });
        res.json({ scripts });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update script
router.put('/registry/:id', authMiddleware, async (req, res) => {
    try {
        const script = await Script.findOne({ 
            _id: req.params.id, 
            user_id: req.user._id
        });
        
        if (!script) {
            return res.status(404).json({ error: 'Script not found or unauthorized' });
        }

        Object.assign(script, req.body);
        script.updated_at = Date.now();
        await script.save();
        
        res.json(script);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Delete script
router.delete('/registry/:id', authMiddleware, async (req, res) => {
    try {
        const script = await Script.findOneAndDelete({ 
            _id: req.params.id, 
            user_id: req.user._id
        });
        
        if (!script) {
            return res.status(404).json({ error: 'Script not found or unauthorized' });
        }
        
        res.json({ message: 'Script deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 
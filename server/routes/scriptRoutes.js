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

// Get script source code
router.get('/registry/:id/source', async (req, res) => {
    try {
        const script = await Script.findById(req.params.id);
        if (!script) {
            return res.status(404).json({ error: 'Script not found' });
        }

        // Send source code as HTML for browser viewing
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${script.name} - Source Code</title>
                <style>
                    pre {
                        background-color: #f5f5f5;
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                    }
                </style>
            </head>
            <body>
                <h1>${script.name}</h1>
                <h3>Source Code:</h3>
                <pre><code>${script.source}</code></pre>
            </body>
            </html>
        `);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get script documentation
router.get('/registry/:id/docs', async (req, res) => {
    try {
        const script = await Script.findById(req.params.id);
        if (!script) {
            return res.status(404).json({ error: 'Script not found' });
        }

        // Send documentation as HTML
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${script.name} - Documentation</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 20px;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    .metadata {
                        background-color: #f5f5f5;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }
                    .requirements {
                        background-color: #f5f5f5;
                        padding: 15px;
                        border-radius: 5px;
                    }
                    .keywords {
                        display: flex;
                        gap: 8px;
                        flex-wrap: wrap;
                    }
                    .keyword {
                        background-color: #e0e0e0;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                </style>
            </head>
            <body>
                <h1>${script.name}</h1>
                
                <div class="metadata">
                    <p><strong>Author:</strong> ${script.author}</p>
                    <p><strong>Version:</strong> ${script.version}</p>
                    <p><strong>Rating:</strong> ${script.rating.toFixed(1)} (${script.num_ratings} ratings)</p>
                    <p><strong>Downloads:</strong> ${script.downloads}</p>
                </div>

                <h2>Description</h2>
                <p>${script.description}</p>

                <h2>Requirements</h2>
                <div class="requirements">
                    <pre>${script.requirements.join('\n')}</pre>
                </div>

                <h2>Keywords</h2>
                <div class="keywords">
                    ${script.keywords.map(keyword => 
                        `<span class="keyword">${keyword}</span>`
                    ).join('')}
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Submit new script (requires authentication)
router.post('/registry', authMiddleware, async (req, res) => {
    console.log(req.user);
    try {
        const script = new Script({
            ...req.body,
            user_id: req.user.id,
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
        const scripts = await Script.find({ user_id: req.user.id });
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
            user_id: req.user.id
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
            user_id: req.user.id
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
const mongoose = require('mongoose');

const ScriptSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        unique: true
    },
    author: {
        type: String,
        required: true
    },
    version: {
        type: String,
        required: true
    },
    description: {
        type: String,
        required: true
    },
    source: {
        type: String,
        required: true
    },
    requirements: {
        type: [String],
        default: []
    },
    keywords: {
        type: [String],
        default: []
    },
    downloads: {
        type: Number,
        default: 0
    },
    rating: {
        type: Number,
        default: 0
    },
    num_ratings: {
        type: Number,
        default: 0
    },
    documentation_url: String,
    source_url: String,
    created_at: {
        type: Date,
        default: Date.now
    },
    updated_at: {
        type: Date,
        default: Date.now
    },
    user_id: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    is_public: {
        type: Boolean,
        default: true
    }
});

module.exports = mongoose.model('Script', ScriptSchema); 
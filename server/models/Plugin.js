const mongoose = require('mongoose');

const PluginSchema = new mongoose.Schema({
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
    main_file: {
        type: String,
        required: true
    },
    config: {
        type: Object,
        default: {}
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
    repository_url: String,
    created_at: {
        type: Date,
        default: Date.now
    },
    updated_at: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('Plugin', PluginSchema); 
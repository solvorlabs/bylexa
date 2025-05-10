const mongoose = require('mongoose');

// Replace with your MongoDB connection URI
const MONGO_URI = 'mongodb://exploringsolver:aman1234@bylexa-shard-00-00.5nwsh.mongodb.net:27017,bylexa-shard-00-01.5nwsh.mongodb.net:27017,bylexa-shard-00-02.5nwsh.mongodb.net:27017/?ssl=true&replicaSet=atlas-rjeloq-shard-0&authSource=admin&retryWrites=true&w=majority&appName=bylexa';

async function resetPluginCollection() {
    try {
        await mongoose.connect(MONGO_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true
        });

        console.log('✅ Connected to MongoDB.');

        // Drop the collection if it exists
        const collectionExists = await mongoose.connection.db.listCollections({ name: 'plugins' }).hasNext();
        if (collectionExists) {
            await mongoose.connection.db.dropCollection('plugins');
            console.log('🗑️ Dropped existing "plugins" collection.');
        } else {
            console.log('ℹ️ "plugins" collection does not exist. Skipping drop.');
        }

        // Create new (empty) collection by instantiating a dummy document (optional)
    } catch (error) {
        console.error('❌ Error resetting plugin collection:', error);
    } finally {
        await mongoose.disconnect();
        console.log('🔌 Disconnected from MongoDB.');
    }
}

resetPluginCollection();

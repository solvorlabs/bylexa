const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
  },
  password: {
    type: String,
    required: true,
  },
  token: {
    type: String,
  },
});

// Pre-save hook to hash the password before saving
userSchema.pre('save', async function (next) {
  const user = this;

  // Hash the password if it’s modified or new
  if (user.isModified('password')) {
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(user.password, salt);
  }
  next();
});

// Method to generate JWT token for the user
userSchema.methods.generateAuthToken = function () {
  const user = this;
  const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, {
    expiresIn: '1h',
  });

  // Save the token in the user’s document
  user.token = token;
  return token;
};

// Method to compare user-entered password with stored hashed password
userSchema.methods.comparePassword = async function (enteredPassword) {
  const user = this;
  return await bcrypt.compare(enteredPassword, user.password);
};

const User = mongoose.model('User', userSchema);
module.exports = User;

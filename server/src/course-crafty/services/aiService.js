const { GoogleGenerativeAI } = require('@google/generative-ai');

const genAI = new GoogleGenerativeAI(process.env.API_KEY_12607);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

exports.generateContent = async (prompt) => {
  try {
    const result = await model.generateContent(prompt);
    const generatedContent = result.response.text().trim();
    return generatedContent;
  } catch (error) {
    console.error('Error generating content:', error);
    throw new Error('Failed to generate content');
  }
};

exports.translateContent = async (content, targetLanguage) => {
  const prompt = `Translate the following text into ${targetLanguage}: "${content}"`;
  try {
    const result = await model.generateContent(prompt);
    const translatedContent = result.response.text().trim();
    return translatedContent;
  } catch (error) {
    console.error('Error translating content:', error);
    throw new Error('Failed to translate content');
  }
};

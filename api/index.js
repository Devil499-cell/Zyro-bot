const axios = require('axios');

module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  const { key, type, term } = req.query;

  // Validate API key
  if (key !== 'patel45') {
    return res.status(401).json({
      success: false,
      message: 'Invalid API key'
    });
  }

  // Validate type
  if (!type || type.toUpperCase() !== 'BOMBER') {
    return res.status(400).json({
      success: false,
      message: 'Type must be BOMBER'
    });
  }

  // Validate term format
  if (!term || !term.includes('|')) {
    return res.status(400).json({
      message: 'Use term like number|count',
      success: false
    });
  }

  const [phoneNumber, count] = term.split('|');
  
  // Validate phone number
  if (!/^\d{10}$/.test(phoneNumber)) {
    return res.status(400).json({
      success: false,
      message: 'Invalid phone number. Must be 10 digits.'
    });
  }

  const requestCount = parseInt(count);
  if (isNaN(requestCount) || requestCount < 1 || requestCount > 100) {
    return res.status(400).json({
      success: false,
      message: 'Count must be between 1 and 100'
    });
  }

  try {
    // 🔥 ORIGINAL API CALL - YAHI SE DATA AAYEGA
    const originalApiUrl = `https://all-sigma-pad-api-damo-5-day.vercel.app/api?key=RAJAN99&type=BOMBER&term=${term}`;
    
    const response = await axios.get(originalApiUrl);
    const originalData = response.data;

    // 🔥 ORIGINAL RESPONSE + DEVELOPER NAME
    res.status(200).json({
      data: originalData.data || originalData, // Original API ka data
      success: true,
      term: term,
      type: "BOMBER",
      developer: "@KINGITACHI18"  // 👈 Aapka naam
    });

  } catch (error) {
    // Agar original API fail ho toh
    res.status(500).json({
      success: false,
      message: 'Original API service unavailable',
      error: error.message,
      developer: "@KINGITACHI18"
    });
  }
};

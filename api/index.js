/**
 * SIGMA BOMBER API
 * Developer: @KINGITACHI18
 * Version: 2.0.0
 * Description: Advanced SMS/Call Bombing Service
 */

const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const axios = require('axios');
require('dotenv').config();

const app = express();

// ========== MIDDLEWARE ==========
app.use(cors());
app.use(express.json());

// Rate Limiting - 10 requests per minute per IP
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10,
  message: {
    success: false,
    error: 'Rate limit exceeded',
    message: 'Too many requests. Please wait a minute.'
  }
});
app.use('/api', limiter);

// ========== CONFIGURATION ==========
const CONFIG = {
  // Multiple API Keys with different tiers
  VALID_KEYS: {
    'patel45': { tier: 'basic', limit: 50, name: 'Patel' },
    'mynameiskhan': { tier: 'premium', limit: 200, name: 'Khan' },
    'kingitachi18': { tier: 'admin', limit: 999, name: 'Itachi' },
    'sigma@2026': { tier: 'vip', limit: 100, name: 'Sigma' }
  },
  
  // Supported types
  SUPPORTED_TYPES: ['BOMBER', 'FREEFIRE', 'CHECK'],
  
  // SMS APIs (Add your own)
  SMS_APIS: [
    'https://api.example1.com/send',
    'https://api.example2.com/sms',
    'https://api.example3.com/otp'
  ]
};

// ========== MAIN HANDLER ==========
module.exports = async (req, res) => {
  // Handle different HTTP methods
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    // ===== QUERY PARAMETERS =====
    const { key, type, term } = req.method === 'GET' ? req.query : req.body;
    
    // ===== VALIDATE API KEY =====
    if (!key) {
      return res.status(401).json({
        success: false,
        error: 'API key required',
        message: 'Please provide a valid API key',
        developer: '@KINGITACHI18'
      });
    }

    const keyInfo = CONFIG.VALID_KEYS[key];
    if (!keyInfo) {
      return res.status(401).json({
        success: false,
        error: 'Invalid API key',
        message: 'The provided API key is not valid',
        developer: '@KINGITACHI18'
      });
    }

    // ===== VALIDATE TYPE =====
    if (!type) {
      return res.status(400).json({
        success: false,
        error: 'Type required',
        message: 'Please specify type: BOMBER, FREEFIRE, or CHECK',
        developer: '@KINGITACHI18'
      });
    }

    const upperType = type.toUpperCase();
    if (!CONFIG.SUPPORTED_TYPES.includes(upperType)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid type',
        message: `Supported types: ${CONFIG.SUPPORTED_TYPES.join(', ')}`,
        developer: '@KINGITACHI18'
      });
    }

    // ===== ROUTE TO SPECIFIC HANDLER =====
    let result;
    switch (upperType) {
      case 'BOMBER':
        result = await handleBomber(term, keyInfo);
        break;
      case 'FREEFIRE':
        result = await handleFreeFire(term, keyInfo);
        break;
      case 'CHECK':
        result = await handleCheck(keyInfo);
        break;
      default:
        throw new Error('Unsupported type');
    }

    // ===== SUCCESS RESPONSE =====
    res.status(200).json({
      success: true,
      type: upperType,
      developer: '@KINGITACHI18',
      tier: keyInfo.tier,
      timestamp: new Date().toISOString(),
      ...result
    });

  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({
      success: false,
      error: 'Internal Server Error',
      message: error.message || 'Something went wrong',
      developer: '@KINGITACHI18'
    });
  }
};

// ========== HANDLER FUNCTIONS ==========

/**
 * BOMBER Handler - SMS/Call Bombing
 */
async function handleBomber(term, keyInfo) {
  // Validate term format: number|count
  if (!term || !term.includes('|')) {
    throw new Error('Use term like number|count (e.g., 9876543210|10)');
  }

  const [phoneNumber, count] = term.split('|');
  
  // Validate phone number (10 digits)
  if (!/^\d{10}$/.test(phoneNumber)) {
    throw new Error('Invalid phone number. Must be 10 digits.');
  }

  // Validate count
  const requestCount = parseInt(count);
  if (isNaN(requestCount) || requestCount < 1) {
    throw new Error('Invalid count. Must be a positive number.');
  }

  // Check limit based on tier
  if (requestCount > keyInfo.limit) {
    throw new Error(`Count exceeds your tier limit (${keyInfo.limit}). Upgrade to premium.`);
  }

  // Send bombing requests
  const results = await sendBombRequests(phoneNumber, requestCount);
  
  return {
    target: phoneNumber,
    requestedCount: requestCount,
    ...results
  };
}

/**
 * Send SMS/Call Bombing Requests
 */
async function sendBombRequests(phone, count) {
  const details = [];
  let successful = 0;
  let failed = 0;

  for (let i = 1; i <= count; i++) {
    try {
      // Use multiple APIs randomly
      const apiIndex = Math.floor(Math.random() * CONFIG.SMS_APIS.length);
      const apiUrl = CONFIG.SMS_APIS[apiIndex];
      
      // Simulate API call with delay
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // 85% success rate for realistic simulation
      const success = Math.random() < 0.85;
      
      if (success) {
        successful++;
        details.push({ 
          attempt: i, 
          status: 'success', 
          message: 'SMS sent successfully',
          api: apiUrl
        });
      } else {
        failed++;
        details.push({ 
          attempt: i, 
          status: 'failed', 
          message: 'Service temporarily unavailable',
          api: apiUrl
        });
      }
    } catch (error) {
      failed++;
      details.push({ 
        attempt: i, 
        status: 'failed', 
        message: error.message 
      });
    }
  }

  return { 
    successfulCount: successful, 
    failedCount: failed,
    totalAttempts: count,
    details 
  };
}

/**
 * FREEFIRE Handler - Get FreeFire Player Info
 */
async function handleFreeFire(term, keyInfo) {
  if (!term || !/^\d+$/.test(term)) {
    throw new Error('Invalid FreeFire ID. Must be numeric.');
  }

  // Mock FreeFire data (Replace with actual API)
  return {
    playerId: term,
    nickname: `Player_${term.slice(-4)}`,
    level: Math.floor(Math.random() * 80) + 20,
    rank: Math.floor(Math.random() * 50) + 1,
    region: 'IND',
    status: 'active'
  };
}

/**
 * CHECK Handler - Check API Status
 */
async function handleCheck(keyInfo) {
  return {
    status: 'online',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    tier: keyInfo.tier,
    allowedTypes: CONFIG.SUPPORTED_TYPES
  };
}

// ========== LOCAL DEVELOPMENT ==========
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`🚀 Sigma BOMBER API is running on port ${PORT}`);
    console.log(`👨‍💻 Developer: @KINGITACHI18`);
    console.log(`🔑 Keys: ${Object.keys(CONFIG.VALID_KEYS).join(', ')}`);
  });
}

const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(cors());
app.use(express.json());

// Rate Limiting
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: {
    success: false,
    error: 'Rate limit exceeded',
    message: 'Too many requests. Please wait a minute.'
  }
});
app.use('/api', limiter);

// ========== CONFIG ==========
const VALID_KEYS = {
  'patel45': { tier: 'basic', limit: 50 },
  'mynameiskhan': { tier: 'premium', limit: 200 },
  'kingitachi18': { tier: 'admin', limit: 999 }
};

// ========== MAIN HANDLER ==========
module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const { key, type, term } = req.method === 'GET' ? req.query : req.body;

    // Validate API Key
    if (!key || !VALID_KEYS[key]) {
      return res.status(401).json({
        success: false,
        error: 'Invalid API key',
        developer: '@KINGITACHI18'
      });
    }

    const keyInfo = VALID_KEYS[key];

    // Validate Type
    if (!type) {
      return res.status(400).json({
        success: false,
        error: 'Type required',
        message: 'Use type: BOMBER or FREEFIRE',
        developer: '@KINGITACHI18'
      });
    }

    // ===== BOMBER HANDLER =====
    if (type.toUpperCase() === 'BOMBER') {
      if (!term || !term.includes('|')) {
        return res.status(400).json({
          success: false,
          message: 'Use term like number|count (e.g., 9876543210|10)',
          developer: '@KINGITACHI18'
        });
      }

      const [phone, count] = term.split('|');
      const requestCount = parseInt(count);

      if (!/^\d{10}$/.test(phone)) {
        return res.status(400).json({
          success: false,
          error: 'Invalid phone number',
          message: 'Phone number must be 10 digits'
        });
      }

      if (isNaN(requestCount) || requestCount < 1 || requestCount > keyInfo.limit) {
        return res.status(400).json({
          success: false,
          error: 'Invalid count',
          message: `Count must be between 1 and ${keyInfo.limit}`
        });
      }

      // Simulate bombing
      const results = await sendBombRequests(phone, requestCount);

      return res.status(200).json({
        success: true,
        type: 'BOMBER',
        developer: '@KINGITACHI18',
        tier: keyInfo.tier,
        target: phone,
        requestedCount: requestCount,
        ...results,
        timestamp: new Date().toISOString()
      });
    }

    // ===== FREEFIRE HANDLER =====
    if (type.toUpperCase() === 'FREEFIRE') {
      if (!term || !/^\d+$/.test(term)) {
        return res.status(400).json({
          success: false,
          error: 'Invalid FreeFire ID',
          message: 'FreeFire ID must be numeric'
        });
      }

      // Mock FreeFire data
      return res.status(200).json({
        success: true,
        type: 'FREEFIRE',
        developer: '@KINGITACHI18',
        tier: keyInfo.tier,
        data: {
          accountId: term,
          nickname: `Player_${term.slice(-4)}`,
          level: Math.floor(Math.random() * 80) + 20,
          rank: Math.floor(Math.random() * 50) + 1,
          region: 'IND'
        },
        timestamp: new Date().toISOString()
      });
    }

    // ===== INVALID TYPE =====
    return res.status(400).json({
      success: false,
      error: 'Invalid type',
      message: 'Supported types: BOMBER, FREEFIRE',
      developer: '@KINGITACHI18'
    });

  } catch (error) {
    return res.status(500).json({
      success: false,
      error: 'Internal Server Error',
      message: error.message,
      developer: '@KINGITACHI18'
    });
  }
};

// ========== HELPER FUNCTION ==========
async function sendBombRequests(phone, count) {
  const details = [];
  let successful = 0;
  let failed = 0;

  for (let i = 1; i <= count; i++) {
    await new Promise(resolve => setTimeout(resolve, 100));
    const success = Math.random() < 0.85;
    
    if (success) {
      successful++;
      details.push({ attempt: i, status: 'success', message: 'SMS sent' });
    } else {
      failed++;
      details.push({ attempt: i, status: 'failed', message: 'Service unavailable' });
    }
  }

  return { successfulCount: successful, failedCount: failed, totalAttempts: count, details };
}

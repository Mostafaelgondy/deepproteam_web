const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');
const auth = require('../middleware/auth');

router.post('/', auth(['client', 'dealer', 'admin']), orderController.createOrder);
router.get('/', auth(), orderController.getOrders);

module.exports = router;

const express = require('express');
const router = express.Router();
const productController = require('../controllers/productController');
const auth = require('../middleware/auth');

router.get('/', productController.getAllProducts);
router.get('/:id', productController.getProductById);
router.post('/', auth(['dealer', 'admin']), productController.createProduct);
router.patch('/:id', auth(['dealer', 'admin']), productController.updateProduct);
router.delete('/:id', auth(['dealer', 'admin']), productController.deleteProduct);

module.exports = router;

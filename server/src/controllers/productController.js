const { Product, User } = require('../models');

exports.getAllProducts = async (req, res) => {
    try {
        const products = await Product.findAll({
            include: { model: User, attributes: ['name', 'email'] }
        });
        res.json(products);
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

exports.getProductById = async (req, res) => {
    try {
        const product = await Product.findByPk(req.params.id, {
            include: { model: User, attributes: ['name'] }
        });
        if (!product) return res.status(404).json({ message: 'Product not found' });
        res.json(product);
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

exports.createProduct = async (req, res) => {
    try {
        const { name, description, price, image, category, stock } = req.body;
        const dealerId = req.user.id;

        const product = await Product.create({
            name,
            description,
            price,
            image,
            category,
            stock,
            dealerId
        });

        res.status(201).json(product);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error' });
    }
};

exports.updateProduct = async (req, res) => {
    try {
        const product = await Product.findByPk(req.params.id);
        if (!product) return res.status(404).json({ message: 'Product not found' });

        if (product.dealerId !== req.user.id && req.user.role !== 'admin') {
            return res.status(403).json({ message: 'Not authorized' });
        }

        await product.update(req.body);
        res.json(product);
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

exports.deleteProduct = async (req, res) => {
    try {
        const product = await Product.findByPk(req.params.id);
        if (!product) return res.status(404).json({ message: 'Product not found' });

        if (product.dealerId !== req.user.id && req.user.role !== 'admin') {
            return res.status(403).json({ message: 'Not authorized' });
        }

        await product.destroy();
        res.json({ message: 'Product deleted' });
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

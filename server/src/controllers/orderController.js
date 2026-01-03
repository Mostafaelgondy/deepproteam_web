const { Order, User } = require('../models');

exports.createOrder = async (req, res) => {
    try {
        const { items, total } = req.body;
        const userId = req.user.id;

        const order = await Order.create({
            userId,
            items, // Should be array of objects
            total,
            status: 'pending'
        });

        res.status(201).json(order);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error' });
    }
};

exports.getOrders = async (req, res) => {
    try {
        let where = {};
        if (req.user.role === 'client') {
            where.userId = req.user.id;
        } 
        // Dealers might want to see orders containing their products, but for simplicity
        // we'll let admins see all, clients see theirs. 
        // Implementing dealer view requires filtering items JSON which is complex in SQL.
        // For this demo, Dealers see all orders (or we can skip).
        
        const orders = await Order.findAll({
            where,
            include: { model: User, attributes: ['name', 'email'] },
            order: [['createdAt', 'DESC']]
        });
        res.json(orders);
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

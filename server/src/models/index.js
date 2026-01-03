const sequelize = require('../config/database');
const User = require('./User');
const Product = require('./Product');
const Order = require('./Order');

// Associations
User.hasMany(Order, { foreignKey: 'userId' });
Order.belongsTo(User, { foreignKey: 'userId' });

User.hasMany(Product, { foreignKey: 'dealerId' });
Product.belongsTo(User, { foreignKey: 'dealerId' });

module.exports = {
    sequelize,
    User,
    Product,
    Order
};

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { sequelize } = require('./models');

const authRoutes = require('./routes/auth');
const productRoutes = require('./routes/products');
const orderRoutes = require('./routes/orders');

const app = express();

app.use(cors());
app.use(bodyParser.json());

app.use('/api/auth', authRoutes);
app.use('/api/products', productRoutes);
app.use('/api/orders', orderRoutes);

// Health check
app.get('/', (req, res) => {
    res.send('API is running...');
});

// Sync Database
sequelize.sync({ alter: true }).then(() => {
    console.log('Database synced');
}).catch(err => {
    console.error('Database sync error:', err);
});

module.exports = app;

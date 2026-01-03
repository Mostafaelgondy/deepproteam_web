<?php
$ADMIN_USER = 'admin';
$ADMIN_PASS = 'admin123'; // change this in production

// Toggle data source: when true, read from the Django SQLite DB at project root.
define('USE_SQLITE', true);
define('SQLITE_DB', __DIR__ . '/../../../db.sqlite3');

// Paths to mock JSON files (used when USE_SQLITE is false)
define('PRODUCTS_FILE', __DIR__ . '/../../../mock/products.json');
define('ORDERS_FILE', __DIR__ . '/../../../mock/orders.json');
define('DEALERS_FILE', __DIR__ . '/../../../mock/dealers.json');

?>

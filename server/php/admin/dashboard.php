<?php
require_once __DIR__ . '/auth.php';
require_login();
require_once __DIR__ . '/api.php';

$products = read_json(PRODUCTS_FILE);
$orders = read_json(ORDERS_FILE);
$dealers = read_json(DEALERS_FILE);

include __DIR__ . '/templates/header.php';
?>
<h2>Dashboard</h2>
<div class="cards">
  <div class="card"><strong><?=count($products)?></strong><div>Products</div></div>
  <div class="card"><strong><?=count($orders)?></strong><div>Orders</div></div>
  <div class="card"><strong><?=count($dealers)?></strong><div>Dealers</div></div>
</div>

<?php include __DIR__ . '/templates/footer.php'; ?>

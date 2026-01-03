<?php
if(session_status() !== PHP_SESSION_ACTIVE) session_start();
?>
<!doctype html>
<html><head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Admin Panel</title>
  <link rel="stylesheet" href="style.css" />
</head><body>
<header class="admin-header">
  <div class="wrap">
    <h1>Admin Panel</h1>
    <nav>
      <a href="dashboard.php">Dashboard</a>
      <a href="products.php">Products</a>
      <a href="orders.php">Orders</a>
      <a href="dealers.php">Dealers</a>
      <a href="logout.php">Logout</a>
    </nav>
  </div>
</header>
<main class="wrap">

<?php
require_once __DIR__ . '/auth.php';
require_login();
require_once __DIR__ . '/api.php';

$orders = read_json(ORDERS_FILE);
include __DIR__ . '/templates/header.php';
?>
<h2>Orders</h2>
<table class="list">
  <thead><tr><th>ID</th><th>Customer</th><th>Total</th><th>Status</th><th>Actions</th></tr></thead>
  <tbody>
  <?php foreach($orders as $o): ?>
    <tr>
      <td><?=htmlspecialchars($o['id'] ?? '')?></td>
      <td><?=htmlspecialchars($o['customer'] ?? '')?></td>
      <td><?=htmlspecialchars($o['total'] ?? '')?></td>
      <td><?=htmlspecialchars($o['status'] ?? '')?></td>
      <td>
        <form method="post" action="api.php?action=update_order_status">
          <input type="hidden" name="id" value="<?=htmlspecialchars($o['id'])?>">
          <select name="status">
            <option value="pending">pending</option>
            <option value="processing">processing</option>
            <option value="shipped">shipped</option>
            <option value="completed">completed</option>
          </select>
          <button>Update</button>
        </form>
      </td>
    </tr>
  <?php endforeach; ?>
  </tbody>
</table>

<?php include __DIR__ . '/templates/footer.php'; ?>

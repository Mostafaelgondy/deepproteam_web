<?php
require_once __DIR__ . '/auth.php';
require_login();
require_once __DIR__ . '/api.php';

$products = read_json(PRODUCTS_FILE);
include __DIR__ . '/templates/header.php';
?>
<h2>Products</h2>
<table class="list">
  <thead><tr><th>ID</th><th>Title</th><th>Price</th><th>Actions</th></tr></thead>
  <tbody>
  <?php foreach($products as $p): ?>
    <tr>
      <td><?=htmlspecialchars($p['id'] ?? '')?></td>
      <td><?=htmlspecialchars($p['title'] ?? '')?></td>
      <td><?=htmlspecialchars($p['price'] ?? '')?></td>
      <td>
        <?php if(!defined('USE_SQLITE') || !USE_SQLITE): ?>
        <form method="post" action="api.php?action=delete_product" onsubmit="return confirm('Delete?')">
          <input type="hidden" name="id" value="<?=htmlspecialchars($p['id'])?>">
          <button>Delete</button>
        </form>
        <?php else: ?>
        <button disabled title="Disabled in DB mode">Delete</button>
        <?php endif; ?>
      </td>
    </tr>
  <?php endforeach; ?>
  </tbody>
</table>

<?php if(!defined('USE_SQLITE') || !USE_SQLITE): ?>
<h3>Add Product</h3>
<form id="addProduct">
  <label>Title<br><input name="title" required></label>
  <label>Price<br><input name="price" required></label>
  <button type="submit">Add</button>
</form>

<script>
document.getElementById('addProduct').addEventListener('submit', function(e){
  e.preventDefault();
  const fd = new FormData(e.target);
  const obj = {};
  fd.forEach((v,k)=>obj[k]=v);
  fetch('api.php?action=add_product', {method:'POST', body: JSON.stringify(obj)})
    .then(r=>r.json()).then(()=>location.reload());
});
</script>
<?php else: ?>
<div class="notice">Add / delete operations are disabled when connected to the project DB. Use Django admin.</div>
<?php endif; ?>

<?php include __DIR__ . '/templates/footer.php'; ?>

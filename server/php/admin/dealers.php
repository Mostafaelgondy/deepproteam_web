<?php
require_once __DIR__ . '/auth.php';
require_login();
require_once __DIR__ . '/api.php';

$dealers = read_json(DEALERS_FILE);
include __DIR__ . '/templates/header.php';
?>
<h2>Dealers</h2>
<table class="list">
  <thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
  <tbody>
  <?php foreach($dealers as $d): ?>
    <tr>
      <td><?=htmlspecialchars($d['id'] ?? '')?></td>
      <td><?=htmlspecialchars($d['name'] ?? '')?></td>
      <td><?=htmlspecialchars($d['email'] ?? '')?></td>
    </tr>
  <?php endforeach; ?>
  </tbody>
</table>

<?php include __DIR__ . '/templates/footer.php'; ?>

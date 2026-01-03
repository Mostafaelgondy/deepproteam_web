<?php
require_once __DIR__ . '/auth.php';

if(is_logged_in()){
    header('Location: dashboard.php');
    exit;
}

$error = '';
if($_SERVER['REQUEST_METHOD'] === 'POST'){
    $u = $_POST['username'] ?? '';
    $p = $_POST['password'] ?? '';
    if(login_user($u, $p)){
        header('Location: dashboard.php');
        exit;
    } else {
        $error = 'Invalid credentials';
    }
}
?>
<?php include __DIR__ . '/templates/header.php'; ?>
<h2>Login</h2>
<?php if($error): ?><div class="error"><?=htmlspecialchars($error)?></div><?php endif; ?>
<form method="post">
  <label>Username<br><input name="username" required></label>
  <label>Password<br><input name="password" type="password" required></label>
  <button type="submit">Login</button>
</form>
<?php include __DIR__ . '/templates/footer.php'; ?>

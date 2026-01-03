<?php
require_once __DIR__ . '/helpers.php';

function handle_auth_login() {
    $db = get_db();
    $data = getRequestBody();
    $username = isset($data['username']) ? trim($data['username']) : '';
    $password = isset($data['password']) ? $data['password'] : '';

    if (!$username || !$password) {
        jsonResponse(['error' => 'invalid_credentials'], 400);
    }

    $stmt = $db->prepare('SELECT id, username, password, email, role, is_staff, is_superuser, is_active FROM users WHERE username = :u LIMIT 1');
    $stmt->execute([':u' => $username]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$user) jsonResponse(['error' => 'invalid_credentials'], 401);
    if (!$user['is_active']) jsonResponse(['error' => 'user_inactive'], 403);

    if (!verifyPassword($password, $user['password'])) {
        jsonResponse(['error' => 'invalid_credentials'], 401);
    }

    $payload = [
        'sub' => $user['id'],
        'username' => $user['username'],
        'role' => $user['role'],
        'exp' => time() + ACCESS_TOKEN_EXP
    ];
    $access = generate_jwt($payload);

    unset($user['password']);
    jsonResponse(['access' => $access, 'expires_in' => ACCESS_TOKEN_EXP, 'user' => $user]);
}

function handle_auth_me() {
    $user = require_auth();
    // Return limited user info
    jsonResponse(['user' => $user]);
}

?>

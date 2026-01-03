<?php
// Simple router for the PHP API
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/helpers.php';
require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/admin.php';

$method = $_SERVER['REQUEST_METHOD'];
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Determine path relative to this script
$script = dirname($_SERVER['SCRIPT_NAME']);
$path = substr($uri, strlen($script));
$path = trim($path, '/');
$parts = explode('/', $path);

// Expected routes start with api
if (empty($parts[0]) || $parts[0] !== 'api') {
    jsonResponse(['error' => 'not_found'], 404);
}

// /api/auth/login, /api/auth/me
if (isset($parts[1]) && $parts[1] === 'auth') {
    if (isset($parts[2]) && $parts[2] === 'login' && $method === 'POST') {
        handle_auth_login();
    }
    if (isset($parts[2]) && $parts[2] === 'me' && $method === 'GET') {
        handle_auth_me();
    }
    jsonResponse(['error' => 'auth_route_not_found'], 404);
}

// /api/admin/stats or /api/admin/users
if (isset($parts[1]) && $parts[1] === 'admin') {
    if (isset($parts[2]) && $parts[2] === 'stats' && $method === 'GET') {
        handle_admin_stats();
    }

    if (isset($parts[2]) && $parts[2] === 'users') {
        // /api/admin/users or /api/admin/users/{id}
        $id = isset($parts[3]) && is_numeric($parts[3]) ? intval($parts[3]) : null;
        handle_admin_users($method, $id);
    }
    jsonResponse(['error' => 'admin_route_not_found'], 404);
}

jsonResponse(['error' => 'route_not_implemented'], 501);

?>

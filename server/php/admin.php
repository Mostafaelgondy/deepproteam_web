<?php
require_once __DIR__ . '/helpers.php';

function handle_admin_users($method, $id = null) {
    $db = get_db();
    $current = require_auth();
    if (!is_admin_user_row($current)) jsonResponse(['error' => 'forbidden'], 403);

    if ($method === 'GET' && $id === null) {
        // list users
        $stmt = $db->query('SELECT id, username, email, role, is_staff, is_superuser, is_active, created_at FROM users ORDER BY id DESC');
        $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
        jsonResponse(['users' => $users]);
    }

    if ($method === 'POST' && $id !== null) {
        // determine action by path suffix (approve_dealer, suspend_user, activate_user)
        $action = $_GET['action'] ?? null;
        if (!$action) jsonResponse(['error' => 'missing_action'], 400);

        if ($action === 'approve_dealer') {
            $stmt = $db->prepare('UPDATE users SET role = :role, is_active = 1 WHERE id = :id');
            $stmt->execute([':role' => 'dealer', ':id' => $id]);
            jsonResponse(['ok' => true]);
        }

        if ($action === 'suspend_user') {
            $stmt = $db->prepare('UPDATE users SET is_active = 0 WHERE id = :id');
            $stmt->execute([':id' => $id]);
            jsonResponse(['ok' => true]);
        }

        if ($action === 'activate_user') {
            $stmt = $db->prepare('UPDATE users SET is_active = 1 WHERE id = :id');
            $stmt->execute([':id' => $id]);
            jsonResponse(['ok' => true]);
        }

        jsonResponse(['error' => 'unknown_action'], 400);
    }

    jsonResponse(['error' => 'not_implemented'], 501);
}

function handle_admin_stats() {
    $db = get_db();
    $current = require_auth();
    if (!is_admin_user_row($current)) jsonResponse(['error' => 'forbidden'], 403);

    // basic stats
    $totalRevenue = 0.0;
    try {
        $stmt = $db->query('SELECT SUM(amount) as s FROM transactions');
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        $totalRevenue = $row ? (float)$row['s'] : 0.0;
    } catch (Exception $e) {
        $totalRevenue = 0.0;
    }

    $activeDealers = $db->query("SELECT COUNT(*) as c FROM users WHERE role='dealer' AND is_active=1")->fetch(PDO::FETCH_ASSOC)['c'];
    $pendingApprovals = $db->query("SELECT COUNT(*) as c FROM users WHERE role='dealer' AND is_active=0")->fetch(PDO::FETCH_ASSOC)['c'];

    jsonResponse(['totalRevenue' => $totalRevenue, 'activeDealers' => (int)$activeDealers, 'pendingApprovals' => (int)$pendingApprovals]);
}

?>

<?php
// Run: php migrate.php  (from server/php)
require_once __DIR__ . '/db.php';

$db = get_db();

// Create tables
$db->exec("CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT,
    role TEXT DEFAULT 'client',
    is_staff INTEGER DEFAULT 0,
    is_superuser INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);");

$db->exec("CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL DEFAULT 0,
    currency TEXT DEFAULT 'USD',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);");

// Seed test users (if not exists)
$check = $db->query("SELECT COUNT(*) as c FROM users")->fetch(PDO::FETCH_ASSOC)['c'];
if ($check == 0) {
    $stmt = $db->prepare('INSERT INTO users (username, password, email, role, is_staff, is_superuser, is_active) VALUES (:u, :p, :e, :r, :s, :su, :a)');
    $pwd = password_hash('admin123', PASSWORD_DEFAULT);
    $stmt->execute([':u' => 'admin', ':p' => $pwd, ':e' => 'admin@example.com', ':r' => 'admin', ':s' => 1, ':su' => 1, ':a' => 1]);

    $pwd = password_hash('dealer123', PASSWORD_DEFAULT);
    $stmt->execute([':u' => 'dealer1', ':p' => $pwd, ':e' => 'dealer1@example.com', ':r' => 'dealer', ':s' => 0, ':su' => 0, ':a' => 1]);

    $pwd = password_hash('client123', PASSWORD_DEFAULT);
    $stmt->execute([':u' => 'client1', ':p' => $pwd, ':e' => 'client1@example.com', ':r' => 'client', ':s' => 0, ':su' => 0, ':a' => 1]);

    // Add a few transactions
    $db->exec("INSERT INTO transactions (user_id, amount) VALUES (1, 100.50), (1, 250.00), (3, 49.00);");

    echo "Seeded database with sample users.\n";
} else {
    echo "Database already has $check user(s); migration applied.\n";
}

echo "DB file: " . realpath(__DIR__ . '/data/db.sqlite') . "\n";

?>

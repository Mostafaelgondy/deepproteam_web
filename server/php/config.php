<?php
// Basic configuration for PHP API
define('DB_PATH', __DIR__ . '/data/db.sqlite');
define('JWT_SECRET', 'replace_this_with_a_strong_secret_key');
define('JWT_ALGO', 'HS256');
define('ACCESS_TOKEN_EXP', 3600); // seconds

// Ensure data directory exists
if (!is_dir(__DIR__ . '/data')) {
    mkdir(__DIR__ . '/data', 0755, true);
}

?>

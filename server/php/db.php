<?php
require_once __DIR__ . '/config.php';

function get_db() {
    static $db = null;
    if ($db === null) {
        $dsn = 'sqlite:' . DB_PATH;
        $db = new PDO($dsn);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    return $db;
}

?>

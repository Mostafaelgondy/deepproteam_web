<?php
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/db.php';

// CORS + common headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

function jsonResponse($data, $status = 200) {
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    exit;
}

function getRequestBody() {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

function getBearerToken() {
    $headers = getallheaders();
    if (!empty($headers['Authorization'])) {
        $matches = [];
        if (preg_match('/Bearer\s+(.*)$/i', $headers['Authorization'], $matches)) {
            return $matches[1];
        }
    }
    // Some servers provide lowercased key
    if (!empty($headers['authorization'])) {
        $matches = [];
        if (preg_match('/Bearer\s+(.*)$/i', $headers['authorization'], $matches)) {
            return $matches[1];
        }
    }
    return null;
}

function base64UrlEncode($data) {
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

function base64UrlDecode($data) {
    $remainder = strlen($data) % 4;
    if ($remainder) {
        $data .= str_repeat('=', 4 - $remainder);
    }
    return base64_decode(strtr($data, '-_', '+/'));
}

function generate_jwt($payload) {
    $header = ['typ' => 'JWT', 'alg' => JWT_ALGO];
    $header_encoded = base64UrlEncode(json_encode($header));
    $payload_encoded = base64UrlEncode(json_encode($payload));
    $signature = hash_hmac('sha256', "$header_encoded.$payload_encoded", JWT_SECRET, true);
    $signature_encoded = base64UrlEncode($signature);
    return "$header_encoded.$payload_encoded.$signature_encoded";
}

function verify_jwt($token) {
    $parts = explode('.', $token);
    if (count($parts) !== 3) return false;
    list($header_b64, $payload_b64, $sig_b64) = $parts;
    $sig = base64UrlDecode($sig_b64);
    $expected = hash_hmac('sha256', "$header_b64.$payload_b64", JWT_SECRET, true);
    if (!hash_equals($expected, $sig)) return false;
    $payload = json_decode(base64UrlDecode($payload_b64), true);
    if (!is_array($payload)) return false;
    if (isset($payload['exp']) && time() > $payload['exp']) return false;
    return $payload;
}

function require_auth() {
    $token = getBearerToken();
    if (!$token) {
        jsonResponse(['error' => 'missing_token'], 401);
    }
    $payload = verify_jwt($token);
    if (!$payload || empty($payload['sub'])) {
        jsonResponse(['error' => 'invalid_or_expired_token'], 401);
    }
    // Load user from DB
    $db = get_db();
    $stmt = $db->prepare('SELECT id, username, email, role, is_staff, is_superuser, is_active FROM users WHERE id = :id LIMIT 1');
    $stmt->execute([':id' => $payload['sub']]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$user) jsonResponse(['error' => 'user_not_found'], 401);
    if (!$user['is_active']) jsonResponse(['error' => 'user_inactive'], 403);
    return $user;
}

function hashPassword($password) {
    return password_hash($password, PASSWORD_DEFAULT);
}

function verifyPassword($password, $hash) {
    return password_verify($password, $hash);
}

function is_admin_user_row($userRow) {
    // Accepts DB row or payload
    if (!$userRow) return false;
    if (!empty($userRow['is_staff']) || !empty($userRow['is_superuser'])) return true;
    if (!empty($userRow['role']) && $userRow['role'] === 'admin') return true;
    return false;
}

?>

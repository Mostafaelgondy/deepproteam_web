<?php

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

header('Content-Type: application/json; charset=utf-8');

// If configured, use SQLite DB (Django DB) as a read source. Destructive actions
// are disabled when using the Django DB to avoid consistency issues.
function get_sqlite(){
    if(!defined('USE_SQLITE') || !USE_SQLITE) return null;
    $path = SQLITE_DB;
    if(!file_exists($path)) return null;
    try{
        $pdo = new PDO('sqlite:' . $path);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $pdo;
    }catch(Exception $e){
        return null;
    }
}

function read_json($path){
    // When SQLite is enabled, translate to DB reads
    $pdo = get_sqlite();
    if($pdo){
        // Map known files to SQL queries
        if(strpos($path, 'products.json') !== false){
            $stmt = $pdo->query("SELECT id, name AS title, COALESCE(price_egp, price_gold, price_mass) AS price, status FROM products_product ORDER BY id DESC");
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
        }
        if(strpos($path, 'orders.json') !== false){
            // Join with user to get username
            $stmt = $pdo->query("SELECT o.id, u.username AS customer, o.total_amount AS total, o.status FROM orders_order o LEFT JOIN accounts_user u ON o.user_id = u.id ORDER BY o.id DESC");
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
        }
        if(strpos($path, 'dealers.json') !== false){
            // users table lives under accounts_user, role column stores dealer/client/admin
            $stmt = $pdo->prepare("SELECT u.id, u.username AS name, u.email FROM accounts_user u WHERE u.role = :role ORDER BY u.id DESC");
            $stmt->execute([':role'=>'dealer']);
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
        }
        return [];
    }

    if(!file_exists($path)) return [];
    $data = file_get_contents($path);
    $arr = json_decode($data, true);
    return is_array($arr) ? $arr : [];
}

function write_json($path, $arr){
    $tmp = json_encode($arr, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    file_put_contents($path, $tmp, LOCK_EX);
}

$action = $_REQUEST['action'] ?? '';

// Listing endpoints (work in both modes)
if($action === 'list_products'){
    echo json_encode(read_json(PRODUCTS_FILE));
    exit;
}

if($action === 'list_orders'){
    echo json_encode(read_json(ORDERS_FILE));
    exit;
}

if($action === 'list_dealers'){
    echo json_encode(read_json(DEALERS_FILE));
    exit;
}

// Protected actions: require login
if(!is_logged_in()){
    http_response_code(401);
    echo json_encode(['error'=>'not_authenticated']);
    exit;
}

// When using SQLite/Django DB, block destructive writes and direct adds.
$pdo = get_sqlite();
if($pdo){
    if(in_array($action, ['add_product','delete_product'])){
        http_response_code(403);
        echo json_encode(['error'=>'disabled_in_sqlite_mode','message'=>'Use Django admin or the backend API to modify DB records.']);
        exit;
    }
}

if($action === 'add_product'){
    $products = read_json(PRODUCTS_FILE);
    $payload = json_decode(file_get_contents('php://input'), true);
    $payload['id'] = time();
    $products[] = $payload;
    write_json(PRODUCTS_FILE, $products);
    echo json_encode(['ok'=>true]);
    exit;
}

if($action === 'delete_product'){
    $id = $_POST['id'] ?? '';
    $products = read_json(PRODUCTS_FILE);
    $products = array_values(array_filter($products, function($p) use ($id){ return strval($p['id']) !== strval($id); }));
    write_json(PRODUCTS_FILE, $products);
    header('Location: products.php');
    exit;
}

if($action === 'update_order_status'){
    $id = $_POST['id'] ?? '';
    $status = $_POST['status'] ?? '';
    // If using SQLite, perform a safe update via SQL
    if($pdo){
        $stmt = $pdo->prepare('UPDATE orders_order SET status = :status WHERE id = :id');
        $stmt->execute([':status'=>$status, ':id'=>$id]);
        header('Location: orders.php');
        exit;
    }
    $orders = read_json(ORDERS_FILE);
    foreach($orders as &$o){ if(strval($o['id']) === strval($id)){ $o['status'] = $status; } }
    write_json(ORDERS_FILE, $orders);
    header('Location: orders.php');
    exit;
}

http_response_code(400);
echo json_encode(['error'=>'unknown_action']);

?>

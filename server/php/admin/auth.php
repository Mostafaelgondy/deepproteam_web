<?php
session_start();
require_once __DIR__ . '/config.php';

function is_logged_in(){
    return !empty($_SESSION['admin_logged_in']);
}

function require_login(){
    if(!is_logged_in()){
        header('Location: login.php');
        exit;
    }
}

function login_user($username, $password){
    global $ADMIN_USER, $ADMIN_PASS;
    if($username === $ADMIN_USER && $password === $ADMIN_PASS){
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['admin_user'] = $username;
        return true;
    }
    return false;
}

function logout_user(){
    session_unset();
    session_destroy();
}

?>

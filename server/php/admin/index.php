<?php
// Redirect to login or dashboard
require_once __DIR__ . '/auth.php';
if(is_logged_in()) header('Location: dashboard.php'); else header('Location: login.php');
exit;

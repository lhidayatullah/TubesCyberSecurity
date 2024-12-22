<?php
    include 'app.php'; 

    if ($_SESSION['user']['role'] !== 'admin') {
        echo "Unauthorized access. You do not have permission to perform this action.";
        exit();
    }

    if (isset($_GET['id'])) {
        $id = $_GET['id'];
        deleteStudent($id);
    }

?>
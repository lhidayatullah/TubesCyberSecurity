<?php
session_start();

// Dummy user credentials for demonstration
$AUTHORIZED_USERS = [
    ['username' => 'admin', 'password' => 'adminpass', 'role' => 'admin'],
    ['username' => 'viewer', 'password' => 'viewerpass', 'role' => 'viewer']
];

// Check if the form is submitted
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];
    $user = null;

    // Validate credentials
    foreach ($AUTHORIZED_USERS as $u) {
        if ($u['username'] === $username && $u['password'] === $password) {
            $user = $u;
            break;
        }
    }

    if ($user) {
        $_SESSION['user'] = $user; // Store user data in the session
        if ($user['role'] === 'admin') {
            header('Location: index.php'); // Redirect to admin dashboard
        } elseif ($user['role'] === 'viewer') {
            header('Location: viewer_dashboard.php'); // Redirect to viewer dashboard
        }
        exit();
    } else {
        $error = 'Invalid username or password!';
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <h2 class="text-center">Login</h2>
                <?php if (!empty($error)): ?>
                    <div class="alert alert-danger" role="alert">
                        <?php echo $error; ?>
                    </div>
                <?php endif; ?>
                <form method="POST" action="login.php">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

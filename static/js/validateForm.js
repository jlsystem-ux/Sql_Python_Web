function validate() {
    var pass = document.getElementById("password").value;
    var cpass = document.getElementById("cpassword").value;

    // Verificar que las contraseñas no estén vacías
    if (pass === "" || cpass === "") {
        alert("Password fields cannot be empty");
        return false;
    }

    // Verificar que las contraseñas coincidan
    if (pass !== cpass) {
        alert("Passwords do not match");
        return false;
    }

    // Verificar que la contraseña tenga al menos 8 caracteres
    if (pass.length < 8) {
        alert("Password must be at least 8 characters long");
        return false;
    }

    // Validación exitosa
    return true;
}



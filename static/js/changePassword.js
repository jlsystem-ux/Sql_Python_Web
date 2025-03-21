function validate() {
    var pass = document.getElementById("newpassword").value;
    var cpass = document.getElementById("cpassword").value;

    // Verificar que los campos no estén vacíos
    if (pass === "" || cpass === "") {
        alert("Password fields cannot be empty!");
        return false;
    }

    // Verificar que las contraseñas coincidan
    if (pass !== cpass) {
        alert("Passwords do not match!");
        return false;
    }

    // Verificar que la contraseña tenga al menos 8 caracteres
    if (pass.length < 8) {
        alert("Password must be at least 8 characters long!");
        return false;
    }

    // Verificar que la contraseña tenga al menos una letra mayúscula, un número y un carácter especial
    var regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!regex.test(pass)) {
        alert("Password must include at least one uppercase letter, one number, and one special character!");
        return false;
    }

    // Validación exitosa
    return true;
}


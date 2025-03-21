// Inicializar Ace Editor
var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/sql");

// Manejar el botón "Ejecutar Consulta"
document.getElementById("runQuery").addEventListener("click", function () {
    var query = editor.getValue();
    // Simular la ejecución de la consulta
    document.getElementById("queryResult").textContent = "Ejecutando consulta: " + query;
    // Aquí puedes integrar una API para ejecutar consultas reales
});
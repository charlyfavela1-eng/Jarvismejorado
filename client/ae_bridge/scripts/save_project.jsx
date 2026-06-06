// Guarda el proyecto activo
if (app.project && app.project.file) {
    app.project.save();
    alert("Proyecto guardado: " + app.project.file.name);
} else {
    alert("No hay proyecto guardado aun. Usa Archivo > Guardar Como primero.");
}

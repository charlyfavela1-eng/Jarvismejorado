// Lista todas las composiciones del proyecto activo
var msg = "";
if (app.project) {
    var comps = [];
    for (var i = 1; i <= app.project.numItems; i++) {
        var item = app.project.item(i);
        if (item instanceof CompItem) {
            comps.push(item.name + " (" + item.duration.toFixed(2) + "s, " + item.width + "x" + item.height + ")");
        }
    }
    msg = comps.length > 0 ? comps.join("\n") : "Sin composiciones";
} else {
    msg = "No hay proyecto abierto";
}
alert(msg);

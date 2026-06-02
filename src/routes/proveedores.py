import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, Response, session
from src.controllers.proveedores_controller import listar_proveedores, crear_proveedor, actualizar_proveedor, eliminar_proveedor

proveedores_bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")

@proveedores_bp.before_request
def verificar_permisos():
    
    if 'id_usuario' not in session:
        return redirect('/login')
    
    if session.get('rol') != 'Administrador':
        return "Acceso denegado. Esta sección es solo para el Administrador.", 403


@proveedores_bp.route("/", methods=["GET"])
def index():
    proveedores = listar_proveedores()
    return render_template("proveedores.html", proveedores=proveedores)

@proveedores_bp.route("/nuevo", methods=["POST"])
def nuevo():
    crear_proveedor(request.form)
    return redirect(url_for("proveedores.index"))

@proveedores_bp.route("/editar/<int:id>", methods=["POST"])
def editar(id):
    actualizar_proveedor(id, request.form)
    return redirect(url_for("proveedores.index"))

@proveedores_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    eliminar_proveedor(id)
    return redirect(url_for("proveedores.index"))

@proveedores_bp.route("/exportar/csv", methods=["GET"])
def exportar_csv():
    proveedores = listar_proveedores()
    
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    
    writer.writerow(['ID Proveedor', 'Nombre / Razon Social', 'Telefono', 'Direccion'])
    
    
    for prov in proveedores:
        writer.writerow([prov['id_proveedor'], prov['nombre'], prov['telefono'], prov['direccion']])
    
    
    respuesta = Response(output.getvalue(), mimetype="text/csv")
    respuesta.headers["Content-Disposition"] = "attachment; filename=reporte_proveedores.csv"
    
    return respuesta
import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, Response
from src.controllers.proveedores_controller import listar_proveedores, crear_proveedor, actualizar_proveedor, eliminar_proveedor


proveedores_bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")

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
    
    # Crear un archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir la cabecera (los títulos de las columnas)
    writer.writerow(['ID Proveedor', 'Nombre / Razon Social', 'Telefono', 'Direccion'])
    
    # Escribir los datos de la base de datos
    for prov in proveedores:
        writer.writerow([prov['id_proveedor'], prov['nombre'], prov['telefono'], prov['direccion']])
    
    # Preparar la descarga
    respuesta = Response(output.getvalue(), mimetype="text/csv")
    respuesta.headers["Content-Disposition"] = "attachment; filename=reporte_proveedores.csv"
    
    return respuesta
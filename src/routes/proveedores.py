from flask import Blueprint, render_template, request, redirect, url_for
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
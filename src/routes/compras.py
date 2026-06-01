from flask import Blueprint, render_template, request, redirect, url_for
from src.controllers.compras_controller import listar_todo, crear_compra

compras_bp = Blueprint("compras", __name__, url_prefix="/compras")

@compras_bp.route("/", methods=["GET"])
def index():

    compras, proveedores, medicamentos = listar_todo()
    return render_template(
        "compras.html",
        compras=compras,
        proveedores=proveedores,
        medicamentos=medicamentos
    )

@compras_bp.route("/nueva", methods=["POST"])
def nueva():

    crear_compra(request.form)
    return redirect(url_for("compras.index"))
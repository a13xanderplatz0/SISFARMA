# src/routes/compras.py
from flask import Blueprint, render_template, request, redirect, url_for, session # <-- Agregamos session
from src.controllers.compras_controller import listar_todo, crear_compra

compras_bp = Blueprint("compras", __name__, url_prefix="/compras")

# 🛡️ Guardián de seguridad absoluto para Compras
@compras_bp.before_request
def verificar_permisos():
    # 1. Validación: Si no hay sesión, al login
    if 'id_usuario' not in session:
        return redirect('/login')
    # 2. Candado: Si no es Administrador, rebota
    if session.get('rol') != 'Administrador':
        return "Acceso denegado. Esta sección es solo para el Administrador.", 403


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
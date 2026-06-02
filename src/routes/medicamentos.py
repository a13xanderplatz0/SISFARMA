# src/routes/medicamentos.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from src.controllers.medicamentos_controller import listar, crear, obtener, actualizar, eliminar

medicamentos_bp = Blueprint("medicamentos", __name__, url_prefix="/medicamentos")

@medicamentos_bp.route("/", methods=["GET"])
def index():

    if 'id_usuario' not in session:
        return redirect('/login')

    medicamentos, categorias = listar()
    return render_template(
        "medicamentos.html",
        medicamentos=medicamentos,
        categorias=categorias,
    )

@medicamentos_bp.route("/nuevo", methods=["POST"])
def nuevo():

    if session.get('rol') != 'Administrador':
        return "Acceso denegado. Solo administradores pueden crear medicamentos.", 403
        
    crear(request.form)
    return redirect(url_for("medicamentos.index"))

@medicamentos_bp.route("/editar/<int:id_medicamento>", methods=["GET"])
def editar(id_medicamento):

    if session.get('rol') != 'Administrador':
        return "Acceso denegado. Solo administradores pueden editar medicamentos.", 403
        
    medicamento = obtener(id_medicamento)
    if not medicamento:
        return redirect(url_for("medicamentos.index"))
    _, categorias = listar()
    return render_template(
        "medicamento_form.html",
        medicamento=medicamento,
        categorias=categorias,
        action_url=url_for("medicamentos.editar", id_medicamento=id_medicamento),
    )

@medicamentos_bp.route("/editar/<int:id_medicamento>", methods=["POST"])
def actualizar_medicamento(id_medicamento):
    if session.get('rol') != 'Administrador':
        return "Acceso denegado.", 403
        
    actualizar(id_medicamento, request.form)
    return redirect(url_for("medicamentos.index"))

@medicamentos_bp.route("/eliminar/<int:id_medicamento>", methods=["POST"])
def borrar(id_medicamento):
    if session.get('rol') != 'Administrador':
        return "Acceso denegado.", 403
        
    eliminar(id_medicamento)
    return redirect(url_for("medicamentos.index"))
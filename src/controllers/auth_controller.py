from functools import wraps

from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import check_password_hash

from src.models.usuario_model import buscar_usuario_por_nombre

auth_ctrl = Blueprint("auth_ctrl", __name__)


def login_requerido(vista):
    """Decorador: redirige a /login si no hay sesión activa."""

    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("auth_ctrl.login"))
        return vista(*args, **kwargs)

    return envoltura


def usuario_actual():
    """Devuelve el usuario de la sesión en formato para las plantillas."""
    u = session.get("usuario")
    if not u:
        return None
    return {"nombre": u["nombre"], "rol": u["rol"]}


@auth_ctrl.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("usuario"):
            if session["usuario"]["rol"] == "Administrador":
                return redirect("/medicamentos")
            return redirect("/ventas")
        return render_template("login.html")

    nombre = request.form["nombre"]
    contrasena = request.form["contrasena"]

    usuario_db = buscar_usuario_por_nombre(nombre)

    if usuario_db and check_password_hash(usuario_db["contrasena"], contrasena):
        session["usuario"] = {
            "id": usuario_db["id_usuario"],
            "nombre": usuario_db["nombre"],
            "rol": usuario_db["rol"],
        }

        if usuario_db["rol"] == "Administrador":
            return redirect("/medicamentos")
        return redirect("/ventas")

    return render_template("login.html", error="Credenciales incorrectas")


@auth_ctrl.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_ctrl.login"))

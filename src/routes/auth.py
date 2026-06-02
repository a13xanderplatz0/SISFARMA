from flask import Blueprint, render_template, request, redirect, url_for, session
from src.controllers.auth_controller import verificar_credenciales

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre")
        contrasena = request.form.get("contrasena")
        
        usuario = verificar_credenciales(nombre, contrasena)
        
        if usuario:
            
            session["id_usuario"] = usuario["id_usuario"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            return redirect("/medicamentos")
        else:
            error = "Usuario o contraseña incorrectos."
            
    return render_template("login.html", error=error)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
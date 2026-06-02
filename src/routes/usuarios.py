import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, Response, session

from src.controllers.usuarios_controller import (
    listar_usuarios_y_administradores,
    crear_usuario,
    actualizar_usuario,
    eliminar_usuario_seguro,
    obtener_reporte_rendimiento_personal
)

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuarios_bp.before_request
def verificar_permisos():
    
    if 'id_usuario' not in session:
        return redirect('/login')
    
    if session.get('rol') != 'Administrador':
        return "Acceso denegado. Esta sección es solo para el Administrador.", 403

@usuarios_bp.route("/", methods=["GET"])
def index():
    usuarios, administradores = listar_usuarios_y_administradores()
    return render_template(
        "usuarios.html",
        usuarios=usuarios,
        administradores=administradores
    )

@usuarios_bp.route("/nuevo", methods=["POST"])
def nuevo():
    nombre = request.form.get("nombre")
    rol = request.form.get("rol")
    contrasena = request.form.get("contrasena")
    id_supervisor = request.form.get("id_supervisor")
    
    # Si viene vacio en el formulario, es None
    if not id_supervisor or id_supervisor == "":
        id_supervisor = None
        
    crear_usuario(
        nombre=nombre,
        rol=rol,
        contrasena=contrasena,
        id_supervisor=id_supervisor
    )
    return redirect(url_for("usuarios.index"))

@usuarios_bp.route("/editar/<int:id_usuario>", methods=["POST"])
def editar(id_usuario):
    nombre = request.form.get("nombre")
    rol = request.form.get("rol")
    contrasena = request.form.get("contrasena")
    id_supervisor = request.form.get("id_supervisor")
    
    if not id_supervisor or id_supervisor == "":
        id_supervisor = None
        
    actualizar_usuario(
        id_usuario=id_usuario,
        nombre=nombre,
        rol=rol,
        contrasena=contrasena,
        id_supervisor=id_supervisor
    )
    return redirect(url_for("usuarios.index"))

@usuarios_bp.route("/eliminar/<int:id_usuario>", methods=["POST"])
def eliminar(id_usuario):
    id_receptor = request.form.get("id_receptor")
    if not id_receptor:
        return "El colaborador receptor es obligatorio para reasignar tareas", 400
        
    try:
        eliminar_usuario_seguro(
            id_usuario_baja=id_usuario,
            id_usuario_receptor=int(id_receptor)
        )
    except Exception as e:
        return f"Error al eliminar colaborador: {str(e)}", 500
        
    return redirect(url_for("usuarios.index"))

@usuarios_bp.route("/reporte/exportar", methods=["GET"])
def exportar_reporte():
    try:
        min_ventas_raw = request.args.get("min_ventas", "1")
        try:
            min_ventas = int(min_ventas_raw)
        except ValueError:
            min_ventas = 1
            
        reporte_data = obtener_reporte_rendimiento_personal(min_ventas)
        
        si = StringIO()
        si.write('\ufeff') # Excel en Windows
        cw = csv.writer(si)
        
        cw.writerow([
            "ID Colaborador",
            "Nombre Colaborador",
            "Rol",
            "Supervisor",
            "Total Ventas Atendidas",
            "Monto Total Vendido (S/)",
            "Total Compras Registradas"
        ])
        
        for row in reporte_data:
            cw.writerow([
                row["id_usuario"],
                row["usuario_nombre"],
                row["usuario_rol"],
                row["supervisor_nombre"] or "Ninguno",
                row["total_ventas_atendidas"],
                f"{float(row['monto_total_vendido']):.2f}",
                row["total_compras_registradas"]
            ])
            
        response = Response(si.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename=reporte_rendimiento_personal_min_{min_ventas}.csv"
        return response
    except Exception as e:
        return f"Error al generar reporte: {str(e)}", 500
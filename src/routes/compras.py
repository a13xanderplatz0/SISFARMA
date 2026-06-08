from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify 
from src.controllers.compras_controller import listar_todo, crear_compra, recibir_compra, anular_compra, obtener_detalle_compra

compras_bp = Blueprint("compras", __name__, url_prefix="/compras")


@compras_bp.before_request
def verificar_permisos():
   
    if 'id_usuario' not in session:
        return redirect('/login')
    
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

@compras_bp.route("/detalle/<int:id_compra>")
def detalle(id_compra):

    return jsonify(
        obtener_detalle_compra(id_compra)
    )

@compras_bp.route("/nueva", methods=["POST"])
def nueva():

    crear_compra(
        request.form,
        session["id_usuario"]
    )

    return redirect(
        url_for("compras.index")
    )

@compras_bp.route("/recibir/<int:id_compra>", methods=["POST"])
def recibir(id_compra):

    cantidad_items = int(
        request.form.get(
            "cantidad_items",
            0
        )
    )

    datos_recepcion = []

    for i in range(cantidad_items):

        datos_recepcion.append({
            "id_medicamento":
                request.form.get(
                    f"id_medicamento_{i}"
                ),

            "numero_lote":
                request.form.get(
                    f"numero_lote_{i}"
                ),

            "fecha_vencimiento":
                request.form.get(
                    f"fecha_vencimiento_{i}"
                ),

            "stock_minimo":
                int(
                    request.form.get(
                        f"stock_minimo_{i}",
                        10
                    )
                )
        })  

    recibir_compra(
        id_compra,
        datos_recepcion
    )

    return redirect(
        url_for(
            "compras.index"
        )
    )

@compras_bp.route("/anular/<int:id_compra>", methods=["POST"])
def anular(id_compra):
    anular_compra(id_compra)
    return redirect(url_for("compras.index"))

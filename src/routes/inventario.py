from flask import Blueprint, render_template, request, redirect, session

from src.controllers.inventario_controller import (
    listar_inventario,
    actualizar_stock
)

inventario_bp = Blueprint(
    'inventario',
    __name__,
    url_prefix='/inventario'
)


@inventario_bp.route('/')
def index():

    if 'id_usuario' not in session:
        return redirect('/login')

    inventario = listar_inventario()

    return render_template(
        'inventario.html',
        inventario=inventario
    )


@inventario_bp.route('/ingreso', methods=['POST'])
def ingreso():

    if session.get('rol') != 'Administrador':
        return "Acceso denegado", 403

    id_inventario = int(request.form['id_inventario'])
    cantidad = int(request.form['cantidad_ingreso'])

    actualizar_stock(
        id_inventario,
        cantidad
    )

    return redirect('/inventario/')
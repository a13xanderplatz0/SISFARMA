import os

from flask import Flask, render_template, request, redirect

from src.routes.medicamentos import medicamentos_bp
from src.routes.ventas import ventas_bp
from src.routes.compras import compras_bp
from src.routes.usuarios import usuarios_bp

from src.controllers.medicamentos_controller import listar
from src.controllers.compras_controller import listar_inventario_real

# importar otros blueprints...

app = Flask(
    __name__,
    template_folder='src/views/templates',
    static_folder='src/views/static',
)

app.register_blueprint(medicamentos_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(usuarios_bp)


@app.context_processor
def inyectar_usuario():
    return {"current_user": {"nombre": "Carlos Mendoza", "rol": "Administrador"}}


CLIENTES_DB = [
    {"id_cliente": 1, "nombre": "Ana López"},
    {"id_cliente": 2, "nombre": "Pedro Infante"},
    {"id_cliente": 3, "nombre": "Sofía Castro"},
    {"id_cliente": 4, "nombre": "Diego Mendoza"},
    {"id_cliente": 5, "nombre": "Lucía Fernández"},
]

PROVEEDORES_DB = [
    {"id_proveedor": 1, "nombre": "Droguería FarmaSalud S.A."},
    {"id_proveedor": 2, "nombre": "Laboratorios Medicor"},
    {"id_proveedor": 3, "nombre": "Distribuidora BioGénesis"},
    {"id_proveedor": 4, "nombre": "PharmaNorte Perú"},
    {"id_proveedor": 5, "nombre": "Suministros Médicos Globales"},
]


@app.route('/')
def inicio():
    return redirect('/medicamentos')


@app.route('/inventario')
def inventario():
    # Datos reales desde la base de datos (v2)
    inventario_db = listar_inventario_real()

    return render_template(
        'inventario.html',
        inventario=inventario_db,
    )


@app.route('/inventario/ingreso', methods=['POST'])
def inventario_ingreso():
    id_inventario = request.form['id_inventario']
    cantidad = request.form['cantidad_ingreso']
    motivo = request.form['motivo']

    print(f"Ingreso inventario #{id_inventario}: +{cantidad} ({motivo})")

    return redirect('/inventario')





if __name__ == '__main__':
    app.run(debug=True)
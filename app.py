import os
from flask import Flask, render_template, request, redirect
from src.routes.medicamentos import medicamentos_bp
from src.routes.compras import compras_bp
from src.controllers.compras_controller import listar_inventario_real
from src.controllers.medicamentos_controller import listar
# importar otros blueprints...

app = Flask(
    __name__,
    template_folder='src/views/templates',
    static_folder='src/views/static',
)
app.register_blueprint(medicamentos_bp)
app.register_blueprint(compras_bp)
# registrar otros...


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

@app.route('/')
def inicio():
    return redirect('/medicamentos')


@app.route('/inventario')
def inventario():
    # Traemos los datos reales directo de la base de datos en lugar de la lista falsa
    inventario_db = listar_inventario_real()

    return render_template(
        'inventario.html',
        inventario=inventario_db,
    )


@app.route('/ventas')
def ventas():
    ventas_db = [
        {"id_venta": 1, "fecha": "2026-05-21", "cliente_nombre": "Ana López", "usuario_nombre": "Ana Gómez", "total": 35.00},
        {"id_venta": 2, "fecha": "2026-05-21", "cliente_nombre": "Pedro Infante", "usuario_nombre": "Ana Gómez", "total": 15.80},
        {"id_venta": 3, "fecha": "2026-05-21", "cliente_nombre": "Sofía Castro", "usuario_nombre": "Ana Gómez", "total": 120.00},
        {"id_venta": 4, "fecha": "2026-05-21", "cliente_nombre": "Diego Mendoza", "usuario_nombre": "Ana Gómez", "total": 8.50},
        {"id_venta": 5, "fecha": "2026-05-21", "cliente_nombre": "Lucía Fernández", "usuario_nombre": "Ana Gómez", "total": 45.20},
    ]

    medicamentos, _ = listar()
    return render_template(
        'ventas.html',
        ventas=ventas_db,
        clientes=CLIENTES_DB,
        medicamentos=medicamentos,
    )


@app.route('/ventas/nueva', methods=['POST'])
def ventas_nueva():
    id_cliente = request.form['id_cliente']
    id_medicamento = request.form['id_medicamento']
    cantidad = request.form['cantidad']
    metodo_pago = request.form['metodo_pago']

    print(f"Nueva venta: cliente #{id_cliente}, medicamento #{id_medicamento}, cantidad {cantidad}, pago {metodo_pago}")

    return redirect('/ventas')


if __name__ == '__main__':
    app.run(debug=True)

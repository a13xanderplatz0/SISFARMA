import os
from flask import Flask, render_template, request, redirect
from src.routes.medicamentos import medicamentos_bp
from src.controllers.medicamentos_controller import listar
# importar otros blueprints...

app = Flask(
    __name__,
    template_folder='src/views/templates',
    static_folder='src/views/static',
)
app.register_blueprint(medicamentos_bp)
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
    inventario_db = [
        {"id_inventario": 1, "medicamento_nombre": "Paracetamol 500mg", "numero_lote": "LOT001", "stock": 100, "stock_minimo": 20},
        {"id_inventario": 2, "medicamento_nombre": "Amoxicilina 500mg", "numero_lote": "LOT002", "stock": 8, "stock_minimo": 10},
        {"id_inventario": 3, "medicamento_nombre": "Ibuprofeno 400mg", "numero_lote": "LOT003", "stock": 75, "stock_minimo": 15},
        {"id_inventario": 4, "medicamento_nombre": "Vitamina C", "numero_lote": "LOT004", "stock": 0, "stock_minimo": 25},
        {"id_inventario": 5, "medicamento_nombre": "Jarabe para la tos", "numero_lote": "LOT005", "stock": 40, "stock_minimo": 10},
    ]
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


@app.route('/compras')
def compras():
    compras_db = [
        {"id_compra": 1, "fecha": "2026-05-10", "proveedor_nombre": "Droguería FarmaSalud S.A.", "usuario_nombre": "Carlos Mendoza", "estado": "recibida"},
        {"id_compra": 2, "fecha": "2026-05-18", "proveedor_nombre": "Laboratorios Medicor", "usuario_nombre": "Ana Gómez", "estado": "pendiente"},
        {"id_compra": 3, "fecha": "2026-05-21", "proveedor_nombre": "Distribuidora BioGénesis", "usuario_nombre": "Luis Torres", "estado": "anulada"},
        {"id_compra": 4, "fecha": "2026-05-22", "proveedor_nombre": "PharmaNorte Perú", "usuario_nombre": "María Delgado", "estado": "recibida"},
        {"id_compra": 5, "fecha": "2026-05-23", "proveedor_nombre": "Suministros Médicos Globales", "usuario_nombre": "Ana Gómez", "estado": "pendiente"},
    ]

    return render_template(
        'compras.html',
        compras=compras_db,
        proveedores=PROVEEDORES_DB,
    )


@app.route('/compras/nueva', methods=['POST'])
def compras_nueva():
    id_proveedor = request.form['id_proveedor']
    estado = request.form['estado']
    fecha = request.form['fecha']

    print(f"Nueva compra: proveedor #{id_proveedor}, estado {estado}, fecha {fecha}")

    return redirect('/compras')


if __name__ == '__main__':
    app.run(debug=True)
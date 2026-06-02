import os

from flask import Flask, render_template, request, redirect, session

from src.routes.medicamentos import medicamentos_bp
from src.routes.ventas import ventas_bp
from src.routes.compras import compras_bp
from src.routes.usuarios import usuarios_bp
from src.routes.proveedores import proveedores_bp
from src.routes.compras import compras_bp
from src.routes.usuarios import usuarios_bp
from src.routes.auth import auth_bp   

from src.controllers.medicamentos_controller import listar
from src.controllers.compras_controller import listar_inventario_real, actualizar_stock_inventario
from src.controllers.reportes_controller import reportes_bp

# importar otros blueprints...

app = Flask(
    __name__,
    template_folder='src/views/templates',
    static_folder='src/views/static',
)

app.secret_key = "super_secreto_sisfarma_2026"

app.register_blueprint(medicamentos_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(auth_bp)

@app.context_processor
def inyectar_usuario():
    # SI hay un usuario en sesión, pasamos sus datos al HTML
    if 'id_usuario' in session:
        return {"current_user": {"nombre": session['nombre'], "rol": session['rol']}}
    
    # SI NO hay nadie (como cuando estás en la pantalla de login), pasamos None
    # ¡OJO! No uses redirect aquí, solo devuelve el diccionario con None
    return {"current_user": None}

@app.route('/')
def inicio():
    # Si no hay sesión iniciada, lo mandamos al login
    if 'id_usuario' not in session:
        return redirect('/login')
    return redirect('/medicamentos')

CLIENTES_DB = [
    {"id_cliente": 1, "nombre": "Ana López"},
    {"id_cliente": 2, "nombre": "Pedro Infante"},
    {"id_cliente": 3, "nombre": "Sofía Castro"},
    {"id_cliente": 4, "nombre": "Diego Mendoza"},
    {"id_cliente": 5, "nombre": "Lucía Fernández"},
]






@app.route('/inventario')
def inventario():
    # Validación: Si no hay sesión, al login
    if 'id_usuario' not in session:
        return redirect('/login')

    # Datos reales desde la base de datos (v2)
    inventario_db = listar_inventario_real()

    return render_template(
        'inventario.html',
        inventario=inventario_db,
    )


@app.route('/inventario/ingreso', methods=['POST'])
def inventario_ingreso():
    # Candado: Solo Administrador
    if session.get('rol') != 'Administrador':
        return "Acceso denegado. Solo administradores pueden ingresar stock.", 403

    id_inventario = request.form['id_inventario']
    cantidad = request.form['cantidad_ingreso']
    motivo = request.form['motivo']

    print(f"Ingreso inventario #{id_inventario}: +{cantidad} ({motivo})")

    return redirect('/inventario')

if __name__ == '__main__':
    app.run(debug=True)
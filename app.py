import os

from flask import Flask, render_template, request, redirect, session

from src.routes.medicamentos import medicamentos_bp
from src.routes.ventas import ventas_bp
from src.routes.compras import compras_bp
from src.routes.usuarios import usuarios_bp
from src.routes.proveedores import proveedores_bp
from src.routes.inventario import inventario_bp
from src.routes.auth import auth_bp   

from src.controllers.reportes_controller import reportes_bp
from src.database.setup import init_database


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
app.register_blueprint(inventario_bp)
app.register_blueprint(auth_bp)

@app.context_processor
def inyectar_usuario():
    
    if 'id_usuario' in session:
        return {"current_user": {"nombre": session['nombre'], "rol": session['rol']}}
    
    
    return {"current_user": None}

@app.route('/')
def inicio():
    
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


if __name__ == '__main__':
    init_database()
    app.run(debug=True)
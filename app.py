from flask import Flask, render_template, request, redirect
# Asumiendo que tienes un archivo donde manejas tus SELECTs a MySQL
# from database import obtener_medicamentos_con_categorias, obtener_todas_las_categorias

app = Flask(
    __name__,
    template_folder='src/views/templates',
    static_folder='src/views/static',
)


@app.route('/')
def inicio():
    return redirect('/medicamentos')


@app.route('/medicamentos')
def catalogo_medicamentos():
    medicamentos_db = [
        {"id_medicamento": 1, "nombre": "Paracetamol 500mg", "descripcion": "Alivia dolor y fiebre", "categoria_nombre": "Analgésicos", "precio": 5.50},
        {"id_medicamento": 2, "nombre": "Amoxicilina 500mg", "descripcion": "Antibiótico de amplio espectro", "categoria_nombre": "Antibióticos", "precio": 12.90},
    ]
    categorias_db = [
        {"id_categoria": 1, "nombre": "Analgésicos"},
        {"id_categoria": 2, "nombre": "Antibióticos"},
    ]
    usuario_sesion = {"nombre": "Carlos Mendoza", "rol": "Administrador"}

    return render_template(
        'medicamentos.html',
        medicamentos=medicamentos_db,
        categorias=categorias_db,
        current_user=usuario_sesion,
    )


@app.route('/medicamentos/nuevo', methods=['POST'])
def nuevo_medicamento():
    nombre = request.form['nombre']
    precio = request.form['precio']
    id_categoria = request.form['id_categoria']
    descripcion = request.form['descripcion']

    print(f"Guardando: {nombre}, Precio: {precio}, Categoría: {id_categoria}, Descripción: {descripcion}")

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
    usuario_sesion = {"nombre": "Carlos Mendoza", "rol": "Administrador"}

    return render_template(
        'inventario.html',
        inventario=inventario_db,
        current_user=usuario_sesion,
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

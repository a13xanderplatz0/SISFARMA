MEDICAMENTOS_DB = [
    {"id_medicamento": 1, "nombre": "Paracetamol 500mg", "descripcion": "Alivia dolor y fiebre", "categoria_nombre": "Analgésicos", "precio": 5.50},
    {"id_medicamento": 2, "nombre": "Amoxicilina 500mg", "descripcion": "Antibiótico de amplio espectro", "categoria_nombre": "Antibióticos", "precio": 12.90},
    {"id_medicamento": 3, "nombre": "Ibuprofeno 400mg", "descripcion": "Antiinflamatorio y analgésico", "categoria_nombre": "Antiinflamatorios", "precio": 8.70},
    {"id_medicamento": 4, "nombre": "Vitamina C", "descripcion": "Suplemento vitamínico", "categoria_nombre": "Vitaminas", "precio": 15.00},
    {"id_medicamento": 5, "nombre": "Jarabe para la tos", "descripcion": "Jarabe expectorante", "categoria_nombre": "Jarabes", "precio": 18.50},
]

CATEGORIAS_DB = [
    {"id_categoria": 1, "nombre": "Analgésicos"},
    {"id_categoria": 2, "nombre": "Antibióticos"},
    {"id_categoria": 3, "nombre": "Antiinflamatorios"},
    {"id_categoria": 4, "nombre": "Vitaminas"},
    {"id_categoria": 5, "nombre": "Jarabes"},
]


def listar():
    return MEDICAMENTOS_DB, CATEGORIAS_DB


def crear(form):
    nombre = form.get('nombre', '').strip()
    precio = float(form.get('precio') or 0)
    id_categoria = int(form.get('id_categoria') or 0)
    descripcion = form.get('descripcion', '').strip()

    categoria_nombre = next(
        (categoria['nombre'] for categoria in CATEGORIAS_DB if categoria['id_categoria'] == id_categoria),
        'Sin categoría'
    )

    nuevo_id = max((medicamento['id_medicamento'] for medicamento in MEDICAMENTOS_DB), default=0) + 1
    nuevo_medicamento = {
        'id_medicamento': nuevo_id,
        'nombre': nombre,
        'descripcion': descripcion,
        'categoria_nombre': categoria_nombre,
        'precio': precio,
    }
    MEDICAMENTOS_DB.append(nuevo_medicamento)
    return nuevo_medicamento


def obtener(id_medicamento):
    return next(
        (medicamento for medicamento in MEDICAMENTOS_DB if medicamento['id_medicamento'] == id_medicamento),
        None
    )


def actualizar(id_medicamento, form):
    medicamento = obtener(id_medicamento)
    if not medicamento:
        return None

    medicamento['nombre'] = form.get('nombre', medicamento['nombre']).strip()
    medicamento['descripcion'] = form.get('descripcion', medicamento['descripcion']).strip()
    medicamento['precio'] = float(form.get('precio') or medicamento['precio'])
    id_categoria = int(form.get('id_categoria') or 0)
    medicamento['categoria_nombre'] = next(
        (categoria['nombre'] for categoria in CATEGORIAS_DB if categoria['id_categoria'] == id_categoria),
        medicamento['categoria_nombre']
    )
    return medicamento


def eliminar(id_medicamento):
    global MEDICAMENTOS_DB
    MEDICAMENTOS_DB = [
        medicamento for medicamento in MEDICAMENTOS_DB
        if medicamento['id_medicamento'] != id_medicamento
    ]
    return True

from werkzeug.security import generate_password_hash

# Datos de prueba hasta conectar MySQL (misma lógica que en schema.sql)
_USUARIOS = [
    {
        "id_usuario": 1,
        "nombre": "Carlos Mendoza",
        "rol": "Administrador",
        "contrasena": generate_password_hash("admin123"),
    },
    {
        "id_usuario": 2,
        "nombre": "Ana Gómez",
        "rol": "Farmacéutico",
        "contrasena": generate_password_hash("farma123"),
    },
]


def buscar_usuario_por_nombre(nombre):
    """Busca usuario por nombre. Reemplazar con SELECT a MySQL cuando conecten la BD."""
    nombre = nombre.strip()
    for usuario in _USUARIOS:
        if usuario["nombre"].lower() == nombre.lower():
            return usuario
    return None

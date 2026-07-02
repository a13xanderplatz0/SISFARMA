from werkzeug.security import check_password_hash
from src.database.connection import execute_query


def verificar_credenciales(nombre, contrasena):
    query = """
        SELECT id_usuario, nombre, rol, contrasena
        FROM USUARIO
        WHERE nombre = %s
    """

    usuario = execute_query(query, (nombre,), fetch_one=True)

    if usuario is None:
        return None

    if check_password_hash(usuario["contrasena"], contrasena):
        return {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "rol": usuario["rol"]
        }

    return None
from src.database.connection import execute_query

def verificar_credenciales(nombre, contrasena):
    
    query = "SELECT id_usuario, nombre, rol FROM USUARIO WHERE nombre = %s AND contrasena = %s"
    resultado = execute_query(query, (nombre, contrasena), fetch_all=True)
    
    if resultado:
        return resultado[0]
    return None
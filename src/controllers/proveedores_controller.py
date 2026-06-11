from src.database.connection import execute_query

def listar_proveedores():
    query = """
        SELECT id_proveedor, nombre, telefono, direccion
        FROM PROVEEDOR
        WHERE activo = TRUE
        ORDER BY id_proveedor DESC
    """
    return execute_query(query, fetch_all=True)

def crear_proveedor(form):
    # Recibe los datos del formulario web, limpia espacios y los inserta
    nombre = form.get('nombre', '').strip()
    telefono = form.get('telefono', '').strip()
    direccion = form.get('direccion', '').strip()
    
    query = "INSERT INTO PROVEEDOR (nombre, telefono, direccion) VALUES (%s, %s, %s)"
    execute_query(query, (nombre, telefono, direccion))
    return True

def actualizar_proveedor(id_proveedor, form):
    nombre = form.get('nombre', '').strip()
    telefono = form.get('telefono', '').strip()
    direccion = form.get('direccion', '').strip()
    
    query = "UPDATE PROVEEDOR SET nombre = %s, telefono = %s, direccion = %s WHERE id_proveedor = %s"
    execute_query(query, (nombre, telefono, direccion, id_proveedor))
    return True

def eliminar_proveedor(id_proveedor):
    query = """
        UPDATE PROVEEDOR
        SET activo = FALSE
        WHERE id_proveedor = %s
    """
    execute_query(query, (id_proveedor,))
    return True
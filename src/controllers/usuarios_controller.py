from werkzeug.security import generate_password_hash
from src.database.connection import get_connection, execute_query

def listar_usuarios_y_administradores():
    usuarios_query = """
        SELECT 
            u.id_usuario, 
            u.nombre, 
            u.rol, 
            u.id_supervisor, 
            s.nombre AS supervisor_nombre
        FROM USUARIO u
        LEFT JOIN USUARIO s ON u.id_supervisor = s.id_usuario
        ORDER BY u.nombre;
    """
    admin_query = "SELECT id_usuario, nombre FROM USUARIO WHERE rol = 'Administrador' ORDER BY nombre"
    
    usuarios = execute_query(usuarios_query, fetch_all=True)
    administradores = execute_query(admin_query, fetch_all=True)
    return usuarios, administradores

def crear_usuario(nombre, rol, contrasena, id_supervisor):
    hashed_pwd = generate_password_hash(contrasena)
    # Si id_supervisor es vacio o 0, guardarlo como None (NULL)
    val_supervisor = int(id_supervisor) if id_supervisor else None
    
    query = "INSERT INTO USUARIO (nombre, rol, contrasena, id_supervisor) VALUES (%s, %s, %s, %s)"
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (nombre.strip(), rol, hashed_pwd, val_supervisor))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()

def actualizar_usuario(id_usuario, nombre, rol, contrasena, id_supervisor):
    val_supervisor = int(id_supervisor) if id_supervisor else None
    
    if contrasena and contrasena.strip():
        hashed_pwd = generate_password_hash(contrasena)
        query = """
            UPDATE USUARIO 
            SET nombre = %s, rol = %s, contrasena = %s, id_supervisor = %s 
            WHERE id_usuario = %s
        """
        params = (nombre.strip(), rol, hashed_pwd, val_supervisor, id_usuario)
    else:
        query = """
            UPDATE USUARIO 
            SET nombre = %s, rol = %s, id_supervisor = %s 
            WHERE id_usuario = %s
        """
        params = (nombre.strip(), rol, val_supervisor, id_usuario)
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()

def eliminar_usuario_seguro(id_usuario_baja, id_usuario_receptor):
    """
    Elimina un usuario de forma segura dentro de una transaccion ACID.
    Transfiere ventas, compras, reportes y supervisados a otro usuario antes de borrar.
    """
    if int(id_usuario_baja) == int(id_usuario_receptor):
        raise ValueError("El colaborador a dar de baja y el receptor de tareas no pueden ser el mismo")
        
    conn = get_connection()
    conn.start_transaction()
    cursor = conn.cursor()
    try:
        # Reasignar todas las ventas atendidas
        cursor.execute(
            "UPDATE VENTA SET id_usuario = %s WHERE id_usuario = %s", 
            (id_usuario_receptor, id_usuario_baja)
        )
        
        # Reasignar todas las compras a proveedores
        cursor.execute(
            "UPDATE COMPRA SET id_usuario = %s WHERE id_usuario = %s", 
            (id_usuario_receptor, id_usuario_baja)
        )
        
        # Reasignar los reportes generados
        cursor.execute(
            "UPDATE REPORTE SET id_usuario = %s WHERE id_usuario = %s", 
            (id_usuario_receptor, id_usuario_baja)
        )
        
        # Actualizar subordinados (reemplazar supervisor)
        cursor.execute(
            "UPDATE USUARIO SET id_supervisor = %s WHERE id_supervisor = %s", 
            (id_usuario_receptor, id_usuario_baja)
        )
        
        # Eliminar fisicamente de la tabla USUARIO
        cursor.execute("DELETE FROM USUARIO WHERE id_usuario = %s", (id_usuario_baja,))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()

def obtener_reporte_rendimiento_personal(min_ventas):
    query = """
        SELECT 
            u.id_usuario,
            u.nombre AS usuario_nombre,
            u.rol AS usuario_rol,
            s.nombre AS supervisor_nombre,
            COUNT(DISTINCT v.id_venta) AS total_ventas_atendidas,
            COALESCE(SUM(v.total), 0) AS monto_total_vendido,
            COUNT(DISTINCT c.id_compra) AS total_compras_registradas
        FROM USUARIO u
        LEFT JOIN USUARIO s ON u.id_supervisor = s.id_usuario
        LEFT JOIN VENTA v ON u.id_usuario = v.id_usuario
        LEFT JOIN COMPRA c ON u.id_usuario = c.id_usuario
        GROUP BY u.id_usuario, u.nombre, u.rol, s.nombre
        HAVING total_ventas_atendidas >= %s
        ORDER BY monto_total_vendido DESC;
    """
    return execute_query(query, (min_ventas,), fetch_all=True)

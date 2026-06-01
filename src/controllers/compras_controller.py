from src.database.connection import get_connection, execute_query

def listar_todo():
    compras_query = """
        SELECT c.id_compra, c.fecha, c.estado, p.nombre AS proveedor_nombre, u.nombre AS usuario_nombre
        FROM COMPRA c
        JOIN PROVEEDOR p ON c.id_proveedor = p.id_proveedor
        JOIN USUARIO u ON c.id_usuario = u.id_usuario
        ORDER BY c.id_compra DESC
    """
    proveedores_query = "SELECT id_proveedor, nombre FROM PROVEEDOR"
    medicamentos_query = "SELECT id_medicamento, nombre FROM MEDICAMENTO"

    compras = execute_query(compras_query, fetch_all=True)
    proveedores = execute_query(proveedores_query, fetch_all=True)
    medicamentos = execute_query(medicamentos_query, fetch_all=True)
    
    return compras, proveedores, medicamentos

def crear_compra(form):
    id_proveedor = int(form.get('id_proveedor') or 0)
    fecha = form.get('fecha')
    estado = form.get('estado')
    id_usuario = 1  # Por defecto el administrador inicial
    
    id_medicamento = int(form.get('id_medicamento') or 0)
    cantidad = int(form.get('cantidad') or 0)
    precio_compra = float(form.get('precio_compra') or 0.0)
    numero_lote = form.get('numero_lote')
    fecha_vencimiento = form.get('fecha_vencimiento')

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            "INSERT INTO COMPRA (fecha, estado, id_proveedor, id_usuario) VALUES (%s, %s, %s, %s)",
            (fecha, estado, id_proveedor, id_usuario)
        )
        id_compra = cursor.lastrowid


        cursor.execute(
            "INSERT INTO DETALLE_COMPRA (precio, cantidad, id_compra, id_medicamento) VALUES (%s, %s, %s, %s)",
            (precio_compra, cantidad, id_compra, id_medicamento)
        )


        if estado == 'recibida':
            
            cursor.execute(
                "INSERT IGNORE INTO LOTE (numero_lote, id_medicamento, fecha_vencimiento) VALUES (%s, %s, %s)",
                (numero_lote, id_medicamento, fecha_vencimiento)
            )

            
            cursor.execute("SELECT id_inventario FROM INVENTARIO WHERE numero_lote = %s AND id_medicamento = %s", (numero_lote, id_medicamento))
            existe = cursor.fetchone()

            if existe:
                
                id_inv = existe[0] if isinstance(existe, tuple) else existe['id_inventario']
                cursor.execute("UPDATE INVENTARIO SET stock = stock + %s WHERE id_inventario = %s", (cantidad, id_inv))
            else:
                
                cursor.execute("INSERT INTO INVENTARIO (stock, stock_minimo, numero_lote, id_medicamento) VALUES (%s, 10, %s, %s)", (cantidad, numero_lote, id_medicamento))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error en la transacción de compra:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def listar_inventario_real():
    
    query = """
        SELECT i.id_inventario, i.stock, i.stock_minimo, i.numero_lote, m.nombre AS medicamento_nombre
        FROM INVENTARIO i
        JOIN MEDICAMENTO m ON i.id_medicamento = m.id_medicamento
        ORDER BY i.id_inventario DESC
    """
    return execute_query(query, fetch_all=True)
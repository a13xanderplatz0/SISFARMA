from datetime import date
from src.database.connection import get_connection, execute_query
from src.models.auditoria_model import registrar_auditoria_venta, registrar_auditoria_anulacion

def listar_productos_y_clientes():
    medicamentos_query = """
        SELECT 
            m.id_medicamento, 
            m.nombre, 
            m.precio, 
            m.descripcion,
            c.nombre AS categoria_nombre,
            COALESCE(SUM(i.stock), 0) AS stock_total
        FROM MEDICAMENTO m
        JOIN CATEGORIA c ON m.id_categoria = c.id_categoria
        LEFT JOIN INVENTARIO i ON m.id_medicamento = i.id_medicamento
        GROUP BY m.id_medicamento, m.nombre, m.precio, m.descripcion, c.nombre
        ORDER BY m.nombre;
    """
    clientes_query = "SELECT id_cliente, nombre, telefono, direccion FROM CLIENTE ORDER BY nombre"
    
    medicamentos = execute_query(medicamentos_query, fetch_all=True)
    clientes = execute_query(clientes_query, fetch_all=True)
    return medicamentos, clientes

def registrar_venta(id_cliente, id_usuario, productos, metodo_pago):
    """
    Registra una venta bajo una transaccion ACID.
    Modifica VENTA, DETALLE_VENTA, PAGO, INVENTARIO e HISTORIAL_VENTA.
    """
    conn = get_connection()
    conn.start_transaction()
    cursor = conn.cursor(dictionary=True)
    try:
        total_venta = 0.0
        detalles_a_insertar = []
        lotes_a_actualizar = []
        
        for prod in productos:
            id_med = int(prod['id_medicamento'])
            cantidad_pedida = int(prod['cantidad'])
            
            if cantidad_pedida <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
            
            # 1. Obtener precio y nombre del medicamento
            cursor.execute("SELECT precio, nombre FROM MEDICAMENTO WHERE id_medicamento = %s", (id_med,))
            med_info = cursor.fetchone()
            if not med_info:
                raise ValueError(f"El medicamento con ID {id_med} no existe")
            precio_unitario = med_info['precio']
            med_nombre = med_info['nombre']
            
            # 2. Obtener lotes de inventario ordenados por fecha de vencimiento (FIFO)
            query_inventario = """
                SELECT i.id_inventario, i.stock, i.numero_lote, l.fecha_vencimiento
                FROM INVENTARIO i
                JOIN LOTE l ON i.numero_lote = l.numero_lote AND i.id_medicamento = l.id_medicamento
                WHERE i.id_medicamento = %s AND i.stock > 0
                ORDER BY l.fecha_vencimiento ASC, i.id_inventario ASC
            """
            cursor.execute(query_inventario, (id_med,))
            lotes = cursor.fetchall()
            
            stock_total = sum(l['stock'] for l in lotes)
            if cantidad_pedida > stock_total:
                raise ValueError(f"Stock insuficiente para {med_nombre}. Solicitado: {cantidad_pedida}, Disponible: {stock_total}")
            
            # 3. Calcular qué lotes se descontaran (FIFO)
            restante = cantidad_pedida
            for lote in lotes:
                if restante <= 0:
                    break
                stock_lote = lote['stock']
                id_inv = lote['id_inventario']
                
                if stock_lote >= restante:
                    lotes_a_actualizar.append((restante, id_inv))
                    restante = 0
                else:
                    lotes_a_actualizar.append((stock_lote, id_inv))
                    restante -= stock_lote
            
            total_venta += float(precio_unitario) * cantidad_pedida
            detalles_a_insertar.append({
                "id_medicamento": id_med,
                "cantidad": cantidad_pedida,
                "precio_unitario": precio_unitario
            })
        
        # B. Insertar cabecera de VENTA
        query_venta = """
            INSERT INTO VENTA (fecha, total, id_cliente, id_usuario)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_venta, (date.today(), total_venta, id_cliente, id_usuario))
        id_venta = cursor.lastrowid
        
        # C. Insertar DETALLE_VENTA y actualizar INVENTARIO
        for det in detalles_a_insertar:
            query_detalle = """
                INSERT INTO DETALLE_VENTA (cantidad, precio_unitario, id_venta, id_medicamento)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_detalle, (det['cantidad'], det['precio_unitario'], id_venta, det['id_medicamento']))
        
        for cant_descuento, id_inv in lotes_a_actualizar:
            query_update_stock = """
                UPDATE INVENTARIO
                SET stock = stock - %s
                WHERE id_inventario = %s
            """
            cursor.execute(query_update_stock, (cant_descuento, id_inv))
        
        # D. Insertar PAGO (Relacion 1:1 con VENTA)
        query_pago = """
            INSERT INTO PAGO (monto, metodo, id_venta)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query_pago, (total_venta, metodo_pago, id_venta))
        
        # E. Insertar HISTORIAL_VENTA
        desc_historial = f"Venta de medicamentos confirmada. Total facturado: S/ {total_venta:.2f}. Metodo: {metodo_pago}."
        query_historial = """
            INSERT INTO HISTORIAL_VENTA (descripcion, id_cliente, id_venta)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query_historial, (desc_historial, id_cliente, id_venta))
        
        conn.commit()

        # ------------------------------------------------------------------
        # AUDITORÍA MONGODB (best-effort — no revierte la venta si falla)
        # ------------------------------------------------------------------
        # Reconstruir info de usuario y cliente para el snapshot
        cursor.execute("SELECT id_usuario, nombre, rol FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
        usr = cursor.fetchone() or {}
        cursor.execute("SELECT id_cliente, nombre, dni, telefono, direccion FROM CLIENTE WHERE id_cliente = %s", (id_cliente,))
        cli = cursor.fetchone() or {}

        # Enriquecer cada producto con nombre y categoría para el snapshot
        productos_snapshot = []
        for det in detalles_a_insertar:
            cursor.execute("""
                SELECT m.nombre, c.nombre AS categoria
                FROM MEDICAMENTO m
                JOIN CATEGORIA c ON m.id_categoria = c.id_categoria
                WHERE m.id_medicamento = %s
            """, (det['id_medicamento'],))
            info = cursor.fetchone() or {}
            # Identificar qué lotes se descontaron para este medicamento
            lotes_med = [
                lote['numero_lote']
                for lote in lotes
                if lote.get('id_inventario') in [l[1] for l in lotes_a_actualizar]
            ]
            productos_snapshot.append({
                "id_medicamento":  det['id_medicamento'],
                "nombre":          info.get('nombre', ''),
                "categoria":       info.get('categoria', ''),
                "cantidad":        det['cantidad'],
                "precio_unitario": float(det['precio_unitario']),
                "subtotal":        float(det['precio_unitario']) * det['cantidad'],
                "lotes_descontados": lotes_med,
            })

        registrar_auditoria_venta(
            id_venta_mysql = id_venta,
            usuario = {
                "id_usuario": usr.get('id_usuario', id_usuario),
                "nombre":     usr.get('nombre', ''),
                "rol":        usr.get('rol', ''),
            },
            cliente = {
                "id_cliente": cli.get('id_cliente', id_cliente),
                "nombre":     cli.get('nombre', ''),
                "dni":        cli.get('dni', ''),
                "telefono":   cli.get('telefono', ''),
                "direccion":  cli.get('direccion', ''),
            },
            productos = productos_snapshot,
            pago = {
                "metodo":      metodo_pago,
                "monto_total": round(total_venta, 2),
            },
            metadata = {"canal": "presencial"},
        )
        # ------------------------------------------------------------------

        return id_venta
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()

def obtener_ventas_historial():
    query = """
        SELECT 
            v.id_venta,
            v.fecha,
            v.total,
            c.nombre AS cliente_nombre,
            u.nombre AS usuario_nombre,
            p.metodo AS metodo_pago
        FROM VENTA v
        JOIN CLIENTE c ON v.id_cliente = c.id_cliente
        JOIN USUARIO u ON v.id_usuario = u.id_usuario
        LEFT JOIN PAGO p ON v.id_venta = p.id_venta
        ORDER BY v.id_venta DESC;
    """
    return execute_query(query, fetch_all=True)

def obtener_detalle_venta(id_venta):
    query_cabecera = """
        SELECT 
            v.id_venta,
            v.fecha,
            v.total,
            c.nombre AS cliente_nombre,
            c.dni AS cliente_dni,
            c.telefono AS cliente_telefono,
            c.direccion AS cliente_direccion,
            u.nombre AS usuario_nombre,
            p.metodo AS metodo_pago,
            hv.descripcion AS historial_descripcion
        FROM VENTA v
        JOIN CLIENTE c ON v.id_cliente = c.id_cliente
        JOIN USUARIO u ON v.id_usuario = u.id_usuario
        LEFT JOIN PAGO p ON v.id_venta = p.id_venta
        LEFT JOIN HISTORIAL_VENTA hv ON v.id_venta = hv.id_venta
        WHERE v.id_venta = %s
    """
    query_detalles = """
        SELECT 
            dv.id_detalle_venta,
            dv.cantidad,
            dv.precio_unitario,
            m.nombre AS medicamento_nombre,
            (dv.cantidad * dv.precio_unitario) AS subtotal
        FROM DETALLE_VENTA dv
        JOIN MEDICAMENTO m ON dv.id_medicamento = m.id_medicamento
        WHERE dv.id_venta = %s
    """
    cabecera = execute_query(query_cabecera, (id_venta,), fetch_one=True)
    if not cabecera:
        return None
    
    detalles = execute_query(query_detalles, (id_venta,), fetch_all=True)
    return {
        "cabecera": cabecera,
        "detalles": detalles
    }

def anular_venta(id_venta):
    """
    Anula una venta: repone el stock y elimina el registro de venta.
    El ON DELETE CASCADE de la base de datos elimina automaticamente
    los registros de DETALLE_VENTA, PAGO y HISTORIAL_VENTA.
    """
    conn = get_connection()
    conn.start_transaction()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Obtener los productos y cantidades de la venta
        cursor.execute("SELECT id_medicamento, cantidad FROM DETALLE_VENTA WHERE id_venta = %s", (id_venta,))
        items = cursor.fetchall()
        
        # 2. Reponer el stock en la primera fila de inventario que coincida
        for item in items:
            id_med = item['id_medicamento']
            cantidad = item['cantidad']
            
            # Buscar el primer lote/registro de inventario activo para este medicamento
            cursor.execute("SELECT id_inventario FROM INVENTARIO WHERE id_medicamento = %s LIMIT 1", (id_med,))
            inv_row = cursor.fetchone()
            if inv_row:
                id_inv = inv_row['id_inventario']
                cursor.execute("UPDATE INVENTARIO SET stock = stock + %s WHERE id_inventario = %s", (cantidad, id_inv))
        
        # 3. Eliminar la venta (provoca borrado en cascada)
        cursor.execute("DELETE FROM VENTA WHERE id_venta = %s", (id_venta,))

        conn.commit()

        # ------------------------------------------------------------------
        # AUDITORÍA MONGODB — registrar anulación (best-effort)
        # ------------------------------------------------------------------
        stock_repuesto_snapshot = [
            {"id_medicamento": it['id_medicamento'], "cantidad": it['cantidad']}
            for it in items
        ]
        registrar_auditoria_anulacion(
            id_venta_mysql = id_venta,
            usuario        = {"id_usuario": 0, "nombre": "Sistema", "rol": "Sistema"},
            motivo         = "Anulación solicitada desde la interfaz",
            stock_repuesto = stock_repuesto_snapshot,
        )
        # ------------------------------------------------------------------

        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()

def crear_cliente_rapido(nombre, dni, telefono, direccion):
    query = "INSERT INTO CLIENTE (nombre, dni, telefono, direccion) VALUES (%s, %s, %s, %s)"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (nombre, dni, telefono, direccion))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        if conn.is_connected():
            conn.close()

def buscar_cliente_por_dni(dni):
    query = "SELECT id_cliente, nombre, dni, telefono, direccion FROM CLIENTE WHERE dni = %s"
    return execute_query(query, (dni,), fetch_one=True)

def obtener_reporte_rendimiento(min_ingreso):
    query = """
        SELECT 
            m.id_medicamento,
            m.nombre AS medicamento_nombre,
            c.nombre AS categoria_nombre,
            SUM(dv.cantidad) AS total_unidades_vendidas,
            SUM(dv.cantidad * dv.precio_unitario) AS ingresos_totales,
            COUNT(DISTINCT v.id_venta) AS cantidad_ventas_realizadas
        FROM MEDICAMENTO m
        JOIN CATEGORIA c ON m.id_categoria = c.id_categoria
        JOIN DETALLE_VENTA dv ON m.id_medicamento = dv.id_medicamento
        JOIN VENTA v ON dv.id_venta = v.id_venta
        GROUP BY m.id_medicamento, m.nombre, c.nombre
        HAVING ingresos_totales >= %s
        ORDER BY ingresos_totales DESC;
    """
    return execute_query(query, (min_ingreso,), fetch_all=True)

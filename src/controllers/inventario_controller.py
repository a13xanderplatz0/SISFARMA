from src.database.connection import execute_query

def listar_inventario():
    query = """
        SELECT
            i.id_inventario,
            m.nombre,
            i.stock,
            i.stock_minimo,
            l.numero_lote,
            l.fecha_vencimiento
        FROM INVENTARIO i
        JOIN MEDICAMENTO m
            ON i.id_medicamento =
            m.id_medicamento
        JOIN LOTE l
            ON i.numero_lote =
            l.numero_lote
        ORDER BY m.nombre;
    """
    return execute_query(query, fetch_all=True)

def actualizar_stock(id_inventario, cantidad):
    query = """
        UPDATE INVENTARIO
        SET stock = stock + %s
        WHERE id_inventario = %s
    """
    execute_query(query, (cantidad, id_inventario))
    return True 
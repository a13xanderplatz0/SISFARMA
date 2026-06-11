from src.database.connection import execute_query


def listar():
    medicamentos_query = """
        SELECT
            m.id_medicamento,
            m.nombre,
            m.precio,
            m.descripcion,
            m.id_categoria,
            c.nombre AS categoria_nombre,
            COALESCE(SUM(i.stock), 0) AS stock_total
        FROM MEDICAMENTO m
        JOIN CATEGORIA c ON m.id_categoria = c.id_categoria
        LEFT JOIN INVENTARIO i ON m.id_medicamento = i.id_medicamento
        WHERE m.activo = 1
        GROUP BY m.id_medicamento, m.nombre, m.precio, m.descripcion, m.id_categoria, c.nombre
        ORDER BY m.id_medicamento
    """
    categorias_query = "SELECT id_categoria, nombre FROM CATEGORIA ORDER BY nombre"
    medicamentos = execute_query(medicamentos_query, fetch_all=True)
    categorias = execute_query(categorias_query, fetch_all=True)
    return medicamentos, categorias


def crear(form):
    nombre = form.get('nombre', '').strip()
    precio = float(form.get('precio') or 0)
    id_categoria = int(form.get('id_categoria') or 0)
    descripcion = form.get('descripcion', '').strip()

    insert_query = "INSERT INTO MEDICAMENTO (nombre, precio, descripcion, id_categoria) VALUES (%s, %s, %s, %s)"
    execute_query(insert_query, (nombre, precio, descripcion, id_categoria))
    return True


def obtener(id_medicamento):
    query = """
        SELECT
            m.id_medicamento,
            m.nombre,
            m.precio,
            m.descripcion,
            m.id_categoria,
            c.nombre AS categoria_nombre
        FROM MEDICAMENTO m
        JOIN CATEGORIA c ON m.id_categoria = c.id_categoria
        WHERE m.id_medicamento = %s
    """
    return execute_query(query, (id_medicamento,), fetch_one=True)


def actualizar(id_medicamento, form):
    nombre = form.get('nombre', '').strip()
    precio = float(form.get('precio') or 0)
    id_categoria = int(form.get('id_categoria') or 0)
    descripcion = form.get('descripcion', '').strip()

    update_query = """
        UPDATE MEDICAMENTO
        SET nombre = %s,
            precio = %s,
            descripcion = %s,
            id_categoria = %s
        WHERE id_medicamento = %s
    """
    execute_query(update_query, (nombre, precio, descripcion, id_categoria, id_medicamento))
    return True


def eliminar(id_medicamento):
    update_query = "UPDATE MEDICAMENTO SET activo = 0 WHERE id_medicamento = %s"
    execute_query(update_query, (id_medicamento,))
    return True

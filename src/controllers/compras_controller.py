from src.database.connection import get_connection
from src.database.connection import execute_query
import json

def listar_todo():
    compras_query = """
        SELECT
            c.id_compra,
            c.fecha,
            c.estado,
            p.nombre AS proveedor_nombre,
            u.nombre AS usuario_nombre
        FROM COMPRA c
        JOIN PROVEEDOR p
            ON c.id_proveedor = p.id_proveedor
        JOIN USUARIO u
            ON c.id_usuario = u.id_usuario
        ORDER BY c.id_compra DESC
    """
    
    proveedores_query = "SELECT id_proveedor, nombre FROM PROVEEDOR WHERE activo = TRUE"
    medicamentos_query = "SELECT id_medicamento, nombre FROM MEDICAMENTO WHERE activo = TRUE"

    compras = execute_query(compras_query, fetch_all=True)
    proveedores = execute_query(proveedores_query, fetch_all=True)
    medicamentos = execute_query(medicamentos_query, fetch_all=True)
    
    return compras, proveedores, medicamentos


def obtener_detalle_compra(id_compra):

    query = """
        SELECT
            d.id_medicamento,
            m.nombre,
            d.cantidad,
            d.precio,
            (d.cantidad * d.precio) AS subtotal
        FROM DETALLE_COMPRA d
        JOIN MEDICAMENTO m
            ON d.id_medicamento = m.id_medicamento
        WHERE d.id_compra = %s
    """

    return execute_query(
        query,
        (id_compra,),
        fetch_all=True
    )


def crear_compra(form, id_usuario):

    id_proveedor = int(
        form.get("id_proveedor")
    )

    fecha = form.get("fecha")

    estado = "pendiente"

    detalle_compra = json.loads(
        form.get("detalle_compra")
    )

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO COMPRA
            (
                fecha,
                estado,
                id_proveedor,
                id_usuario
            )
            VALUES
            (%s,%s,%s,%s)
            """,
            (
                fecha,
                estado,
                id_proveedor,
                id_usuario
            )
        )

        id_compra = cursor.lastrowid

        for item in detalle_compra:

            cursor.execute(
                """
                INSERT INTO DETALLE_COMPRA
                (
                    precio,
                    cantidad,
                    id_compra,
                    id_medicamento
                )
                VALUES
                (%s,%s,%s,%s)
                """,
                (
                    float(item["precio"]),
                    int(item["cantidad"]),
                    id_compra,
                    int(item["id"])
                )
            )

        conn.commit()

        return True

    except Exception as e:

        conn.rollback()

        print(
            "Error en la compra:",
            e
        )

        return False

    finally:

        cursor.close()
        conn.close()

def recibir_compra(id_compra, datos_recepcion):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT estado
            FROM COMPRA
            WHERE id_compra = %s
        """, (id_compra,))

        compra = cursor.fetchone()

        if not compra:
            return False

        if compra["estado"] != "pendiente":
            return False

        cursor.execute("""
            SELECT
                id_medicamento,
                cantidad
            FROM DETALLE_COMPRA
            WHERE id_compra = %s
        """, (id_compra,))

        detalles = cursor.fetchall()

        detalles_map = {
            item["id_medicamento"]: item
            for item in detalles
        }

        for item in datos_recepcion:

            id_medicamento = int(
                item["id_medicamento"]
            )

            cantidad = detalles_map[
                id_medicamento
            ]["cantidad"]

            numero_lote = item[
                "numero_lote"
            ]

            fecha_vencimiento = item[
                "fecha_vencimiento"
            ]

            stock_minimo = item[
                "stock_minimo"
            ]

            cursor.execute("""
                SELECT numero_lote
                FROM LOTE
                WHERE numero_lote = %s
                AND id_medicamento = %s
            """,
            (
                numero_lote,
                id_medicamento
            ))

            if cursor.fetchone():
                raise Exception(
                    f"Lote duplicado: {numero_lote}"
                )

            cursor.execute("""
                INSERT INTO LOTE
                (
                    numero_lote,
                    id_medicamento,
                    fecha_vencimiento
                )
                VALUES (%s, %s, %s)
            """,
            (
                numero_lote,
                id_medicamento,
                fecha_vencimiento
            ))

            cursor.execute("""
                INSERT INTO INVENTARIO
                (
                    stock,
                    stock_minimo,
                    numero_lote,
                    id_medicamento
                )
                VALUES (%s, %s, %s, %s)
            """,
            (
                cantidad,
                stock_minimo,
                numero_lote,
                id_medicamento
            ))

        cursor.execute("""
            UPDATE COMPRA
            SET estado = 'recibida'
            WHERE id_compra = %s
        """, (id_compra,))

        conn.commit()

        return True

    except Exception as e:

        conn.rollback()

        print(
            "Error al recibir compra:",
            e
        )

        return False

    finally:

        cursor.close()
        conn.close()

def anular_compra(id_compra):
    query = """
        UPDATE COMPRA
        SET estado = 'anulada'
        WHERE id_compra = %s
    """

    try:
        execute_query(query, (id_compra,))
        return True

    except Exception as e:
        print("Error al anular compra:", e)
        return False


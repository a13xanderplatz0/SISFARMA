"""
mongo_seed.py
=============
Script de inicialización de datos para MongoDB.

Propósito:
  Lee las ventas históricas ya existentes en MySQL (Railway) y crea los
  documentos de auditoría correspondientes en MongoDB, dejando la base de
  datos lista para que el módulo de auditoría pueda leer y escribir.

Uso:
  python src/database/mongo_seed.py

También se llama automáticamente desde app.py si la colección está vacía.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone, date

# Asegurar que el root del proyecto esté en el path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env', override=True)

from src.database.connection import execute_query
from src.database.mongo_connection import get_collection

# Nombres de colecciones
COL_VENTAS      = "auditoria_ventas"
COL_ANULACIONES = "auditoria_anulaciones"


def _fecha_a_datetime(valor) -> datetime:
    """Convierte un date o string a datetime UTC para MongoDB."""
    if isinstance(valor, datetime):
        return valor.replace(tzinfo=timezone.utc)
    if isinstance(valor, date):
        return datetime(valor.year, valor.month, valor.day, tzinfo=timezone.utc)
    if isinstance(valor, str):
        d = datetime.strptime(valor, "%Y-%m-%d")
        return d.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def seed_auditoria_ventas():
    """
    Lee todas las ventas de MySQL y crea documentos de auditoría en MongoDB.
    Solo inserta ventas que todavía no existan en Mongo (idempotente).
    """
    print("\n[Seed] Cargando ventas históricas de MySQL → MongoDB...")

    # Traer todas las ventas con su información completa
    ventas = execute_query("""
        SELECT
            v.id_venta,
            v.fecha,
            v.total,
            v.id_cliente,
            v.id_usuario,
            c.nombre  AS cliente_nombre,
            c.telefono AS cliente_telefono,
            c.direccion AS cliente_direccion,
            u.nombre  AS usuario_nombre,
            u.rol     AS usuario_rol,
            p.metodo  AS metodo_pago,
            p.monto   AS monto_pago
        FROM VENTA v
        JOIN CLIENTE  c ON v.id_cliente  = c.id_cliente
        JOIN USUARIO  u ON v.id_usuario  = u.id_usuario
        LEFT JOIN PAGO p ON v.id_venta   = p.id_venta
        ORDER BY v.id_venta ASC
    """, fetch_all=True)

    if not ventas:
        print("[Seed] No se encontraron ventas en MySQL.")
        return 0

    col = get_collection(COL_VENTAS)
    insertados = 0
    omitidos   = 0

    for venta in ventas:
        id_venta = venta['id_venta']

        # Idempotente: no duplicar si ya existe
        if col.find_one({"id_venta_mysql": id_venta}):
            omitidos += 1
            continue

        # Traer detalles de los productos de esa venta
        detalles = execute_query("""
            SELECT
                dv.id_medicamento,
                dv.cantidad,
                dv.precio_unitario,
                m.nombre      AS medicamento_nombre,
                cat.nombre    AS categoria_nombre
            FROM DETALLE_VENTA dv
            JOIN MEDICAMENTO m  ON dv.id_medicamento = m.id_medicamento
            JOIN CATEGORIA   cat ON m.id_categoria   = cat.id_categoria
            WHERE dv.id_venta = %s
        """, (id_venta,), fetch_all=True)

        productos_snapshot = []
        for det in detalles:
            # Buscar lotes asociados al medicamento (referencia informativa)
            lotes = execute_query("""
                SELECT DISTINCT i.numero_lote
                FROM INVENTARIO i
                WHERE i.id_medicamento = %s
                LIMIT 3
            """, (det['id_medicamento'],), fetch_all=True)

            lotes_lista = [l['numero_lote'] for l in lotes] if lotes else []

            productos_snapshot.append({
                "id_medicamento":    det['id_medicamento'],
                "nombre":            det['medicamento_nombre'],
                "categoria":         det['categoria_nombre'],
                "cantidad":          det['cantidad'],
                "precio_unitario":   float(det['precio_unitario']),
                "subtotal":          float(det['precio_unitario']) * det['cantidad'],
                "lotes_descontados": lotes_lista,
            })

        documento = {
            "id_venta_mysql": id_venta,
            "fecha":          _fecha_a_datetime(venta['fecha']),
            "registrado_por": {
                "id_usuario": venta['id_usuario'],
                "nombre":     venta['usuario_nombre'],
                "rol":        venta['usuario_rol'],
            },
            "cliente": {
                "id_cliente": venta['id_cliente'],
                "nombre":     venta['cliente_nombre'],
                "telefono":   venta['cliente_telefono'] or '',
                "direccion":  venta['cliente_direccion'] or '',
            },
            "productos": productos_snapshot,
            "pago": {
                "metodo":      venta['metodo_pago'] or 'efectivo',
                "monto_total": float(venta['monto_pago'] or venta['total']),
            },
            "metadata": {
                "canal":   "presencial",
                "origen":  "seed_historico",
                "notas":   "Documento creado por migración inicial desde MySQL",
            },
            "estado": "activa",
        }

        col.insert_one(documento)
        insertados += 1
        print(f"  ✓ Venta #{id_venta} insertada en MongoDB")

    print(f"\n[Seed] Completado: {insertados} insertadas, {omitidos} ya existían.")
    return insertados


def seed_indices():
    """
    Crea índices en las colecciones para optimizar consultas.
    (equivalente a CREATE INDEX en SQL)
    Si Railway no tiene espacio suficiente, los índices se omiten sin error.
    """
    print("\n[Seed] Creando índices en MongoDB...")

    col_ventas      = get_collection(COL_VENTAS)
    col_anulaciones = get_collection(COL_ANULACIONES)

    indices = [
        (col_ventas,      "id_venta_mysql",           {"unique": True,  "name": "idx_id_venta_mysql"}),
        (col_ventas,      [("fecha", -1)],             {"name": "idx_fecha_desc"}),
        (col_ventas,      "estado",                    {"name": "idx_estado"}),
        (col_ventas,      "cliente.id_cliente",        {"name": "idx_cliente"}),
        (col_anulaciones, "id_venta_mysql",            {"name": "idx_anulacion_venta"}),
        (col_anulaciones, [("fecha_anulacion", -1)],   {"name": "idx_anulacion_fecha"}),
    ]

    for col, keys, opts in indices:
        try:
            col.create_index(keys, **opts)
            print(f"  [OK] Indice '{opts['name']}' creado")
        except Exception as e:
            print(f"  [SKIP] Indice '{opts.get('name')}' omitido: {e}")

    print("[Seed] Indices procesados.")




def run_seed():
    """Punto de entrada principal del seed."""
    print("=" * 55)
    print("  SISFARMA — Seed inicial de MongoDB")
    print("=" * 55)

    seed_indices()
    total = seed_auditoria_ventas()

    print("\n[Seed] MongoDB listo.")
    print(f"  Colección '{COL_VENTAS}'      → {get_collection(COL_VENTAS).count_documents({})} docs")
    print(f"  Colección '{COL_ANULACIONES}' → {get_collection(COL_ANULACIONES).count_documents({})} docs")
    print("=" * 55)
    return total


if __name__ == "__main__":
    run_seed()

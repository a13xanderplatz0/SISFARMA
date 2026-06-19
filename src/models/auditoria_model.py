"""
auditoria_model.py
==================
Módulo NoSQL/Híbrido — Auditoría de Ventas en MongoDB.

JUSTIFICACIÓN frente al modelo relacional (MySQL):
  - En MySQL reconstruir una venta histórica requiere JOIN entre 5 tablas
    (VENTA, DETALLE_VENTA, MEDICAMENTO, PAGO, HISTORIAL_VENTA).
  - Si un medicamento cambia de precio/nombre después de la venta, el
    registro relacional ya no refleja el estado real al momento de la
    transacción.
  - MongoDB permite guardar un documento autocontenido (snapshot inmutable)
    con toda la información embebida → consulta en O(1), sin JOINs, y el
    documento conserva exactamente los datos del momento de la venta.
  - El esquema flexible (semi-estructurado) permite agregar campos como
    'receta_medica', 'canal_venta' o 'descuentos' sin ALTER TABLE.

Colecciones utilizadas:
  · auditoria_ventas       — snapshot completo de cada venta registrada
  · auditoria_anulaciones  — registro de cada anulación con snapshot original
"""

from datetime import datetime, timezone
from bson import ObjectId

from src.database.mongo_connection import get_collection


# ---------------------------------------------------------------------------
# Nombres de colecciones
# ---------------------------------------------------------------------------
COL_VENTAS      = "auditoria_ventas"
COL_ANULACIONES = "auditoria_anulaciones"


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _now() -> datetime:
    """Timestamp UTC actual."""
    return datetime.now(timezone.utc)


def _serializar_id(doc: dict) -> dict:
    """Convierte ObjectId a string para poder devolverlo como JSON."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ---------------------------------------------------------------------------
# ESCRITURA — auditoria_ventas
# ---------------------------------------------------------------------------

def registrar_auditoria_venta(
    id_venta_mysql: int,
    usuario: dict,
    cliente: dict,
    productos: list,
    pago: dict,
    metadata: dict | None = None,
) -> str | None:
    """
    Inserta un documento de auditoría completo al momento de registrar
    una venta exitosa en MySQL.

    Parámetros:
        id_venta_mysql  — ID de la venta en MySQL (int)
        usuario         — {"id_usuario": int, "nombre": str, "rol": str}
        cliente         — {"id_cliente": int, "nombre": str, "telefono": str, "direccion": str}
        productos       — [{"id_medicamento": int, "nombre": str, "categoria": str,
                             "cantidad": int, "precio_unitario": float, "subtotal": float,
                             "lotes_descontados": [str]}]
        pago            — {"metodo": str, "monto_total": float}
        metadata        — dict libre con datos adicionales (canal, notas, etc.)

    Retorna el _id del documento insertado como string, o None si falla.
    """
    try:
        col = get_collection(COL_VENTAS)
        documento = {
            "id_venta_mysql":   id_venta_mysql,
            "fecha":            _now(),
            "registrado_por":   usuario,
            "cliente":          cliente,
            "productos":        productos,
            "pago":             pago,
            "metadata":         metadata or {},
            "estado":           "activa",
        }
        resultado = col.insert_one(documento)
        print(f"[MongoDB Auditoría] Venta #{id_venta_mysql} auditada → {resultado.inserted_id}")
        return str(resultado.inserted_id)
    except Exception as exc:
        # La auditoría es best-effort: no revierte la venta de MySQL si falla
        print(f"[MongoDB Auditoría] ADVERTENCIA — no se pudo auditar venta #{id_venta_mysql}: {exc}")
        return None


# ---------------------------------------------------------------------------
# ESCRITURA — auditoria_anulaciones
# ---------------------------------------------------------------------------

def registrar_auditoria_anulacion(
    id_venta_mysql: int,
    usuario: dict,
    motivo: str,
    stock_repuesto: list,
) -> str | None:
    """
    Inserta un documento de anulación y marca la auditoría de venta original
    como 'anulada'.

    Parámetros:
        id_venta_mysql  — ID de la venta anulada en MySQL
        usuario         — {"id_usuario": int, "nombre": str, "rol": str}
        motivo          — Texto libre con la razón de la anulación
        stock_repuesto  — [{"id_medicamento": int, "nombre": str, "cantidad": int}]

    Retorna el _id del documento de anulación como string, o None si falla.
    """
    try:
        col_ventas      = get_collection(COL_VENTAS)
        col_anulaciones = get_collection(COL_ANULACIONES)

        # Obtener el snapshot original para embebido en el documento de anulación
        snapshot_original = col_ventas.find_one({"id_venta_mysql": id_venta_mysql})

        # Marcar la venta original como anulada
        col_ventas.update_one(
            {"id_venta_mysql": id_venta_mysql},
            {"$set": {"estado": "anulada", "fecha_anulacion": _now()}},
        )

        documento_anulacion = {
            "id_venta_mysql":         id_venta_mysql,
            "fecha_anulacion":        _now(),
            "anulado_por":            usuario,
            "motivo":                 motivo,
            "stock_repuesto":         stock_repuesto,
            "snapshot_venta_original": snapshot_original,
        }
        resultado = col_anulaciones.insert_one(documento_anulacion)
        print(f"[MongoDB Auditoría] Anulación de venta #{id_venta_mysql} registrada → {resultado.inserted_id}")
        return str(resultado.inserted_id)
    except Exception as exc:
        print(f"[MongoDB Auditoría] ADVERTENCIA — no se pudo auditar anulación #{id_venta_mysql}: {exc}")
        return None


# ---------------------------------------------------------------------------
# LECTURA — auditoria_ventas
# ---------------------------------------------------------------------------

def obtener_auditoria_por_venta(id_venta_mysql: int) -> dict | None:
    """
    Devuelve el documento de auditoría de una venta específica.
    """
    try:
        col = get_collection(COL_VENTAS)
        doc = col.find_one({"id_venta_mysql": id_venta_mysql})
        return _serializar_id(doc) if doc else None
    except Exception as exc:
        print(f"[MongoDB Auditoría] Error al leer auditoría de venta #{id_venta_mysql}: {exc}")
        return None


def listar_auditorias(limite: int = 20, pagina: int = 1) -> list:
    """
    Lista las auditorías de ventas paginadas, ordenadas de más reciente a más antigua.
    """
    try:
        col  = get_collection(COL_VENTAS)
        skip = (pagina - 1) * limite
        docs = col.find({}).sort("fecha", -1).skip(skip).limit(limite)
        return [_serializar_id(d) for d in docs]
    except Exception as exc:
        print(f"[MongoDB Auditoría] Error al listar auditorías: {exc}")
        return []


def listar_anulaciones(limite: int = 20, pagina: int = 1) -> list:
    """
    Lista los documentos de anulaciones paginados.
    """
    try:
        col  = get_collection(COL_ANULACIONES)
        skip = (pagina - 1) * limite
        docs = col.find({}).sort("fecha_anulacion", -1).skip(skip).limit(limite)
        return [_serializar_id(d) for d in docs]
    except Exception as exc:
        print(f"[MongoDB Auditoría] Error al listar anulaciones: {exc}")
        return []


def contar_auditorias() -> dict:
    """
    Devuelve el conteo total de documentos en cada colección.
    Útil para dashboards o verificación.
    """
    try:
        return {
            "total_ventas":      get_collection(COL_VENTAS).count_documents({}),
            "total_activas":     get_collection(COL_VENTAS).count_documents({"estado": "activa"}),
            "total_anuladas":    get_collection(COL_VENTAS).count_documents({"estado": "anulada"}),
            "total_anulaciones": get_collection(COL_ANULACIONES).count_documents({}),
        }
    except Exception as exc:
        print(f"[MongoDB Auditoría] Error al contar documentos: {exc}")
        return {}

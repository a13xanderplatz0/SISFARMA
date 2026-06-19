"""
verificar_mongo.py
Script para comprobar visualmente que MongoDB tiene datos de auditoria.
Ejecutar con: python verificar_mongo.py
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env', override=True)

from src.database.mongo_connection import get_collection

def verificar():
    col_ventas      = get_collection("auditoria_ventas")
    col_anulaciones = get_collection("auditoria_anulaciones")

    total_v = col_ventas.count_documents({})
    total_a = col_anulaciones.count_documents({})

    sep = "=" * 55
    print()
    print(sep)
    print("  SISFARMA - Verificacion NoSQL MongoDB")
    print(sep)
    print(f"  Coleccion 'auditoria_ventas'     : {total_v} documentos")
    print(f"  Coleccion 'auditoria_anulaciones': {total_a} documentos")
    print(sep)

    if total_v == 0:
        print("  [!] La coleccion esta vacia. Ejecuta el seed primero.")
        return

    print()
    print("  DOCUMENTOS EN auditoria_ventas:")
    print()

    for doc in col_ventas.find({}).sort("id_venta_mysql", 1):
        id_v     = doc.get("id_venta_mysql", "?")
        estado   = doc.get("estado", "?")
        fecha    = doc.get("fecha", "?")
        cliente  = doc.get("cliente", {})
        cajero   = doc.get("registrado_por", {})
        pago     = doc.get("pago", {})
        prods    = doc.get("productos", [])
        metadata = doc.get("metadata", {})
        mongo_id = str(doc.get("_id", ""))

        print(f"  Venta MySQL #{ id_v }  |  Estado: {estado}")
        print(f"    Fecha     : {fecha}")
        print(f"    Cliente   : {cliente.get('nombre')}  |  Tel: {cliente.get('telefono')}")
        print(f"    Cajero    : {cajero.get('nombre')}   Rol: {cajero.get('rol')}")
        print(f"    Pago      : {pago.get('metodo')}  Total: S/ {pago.get('monto_total')}")
        print(f"    Canal     : {metadata.get('canal', '?')}")
        print(f"    Productos : {len(prods)}")
        for p in prods:
            print(f"      * {p.get('nombre')} (x{p.get('cantidad')}) "
                  f"@ S/{p.get('precio_unitario')}  => S/{p.get('subtotal')}")
            print(f"        Categoria: {p.get('categoria')}  |  "
                  f"Lotes: {p.get('lotes_descontados')}")
        print(f"    _id Mongo : {mongo_id}")
        print()

    if total_a > 0:
        print(sep)
        print("  DOCUMENTOS EN auditoria_anulaciones:")
        print()
        for doc in col_anulaciones.find({}).sort("fecha_anulacion", -1):
            print(f"  Anulacion de venta #{doc.get('id_venta_mysql')}")
            print(f"    Fecha    : {doc.get('fecha_anulacion')}")
            print(f"    Motivo   : {doc.get('motivo')}")
            print(f"    _id Mongo: {str(doc.get('_id'))}")
            print()

    print(sep)
    print("  Diferencia clave vs MySQL:")
    print("  > MySQL: necesita JOIN de 5 tablas para reconstruir una venta")
    print("  > MongoDB: 1 documento ya contiene TODO (cliente, productos,")
    print("             precios, lotes, cajero, canal) - snapshot inmutable")
    print(sep)
    print()

if __name__ == "__main__":
    verificar()

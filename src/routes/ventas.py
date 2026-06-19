import csv
from io import StringIO
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, Response

from src.controllers.ventas_controller import (
    listar_productos_y_clientes,
    registrar_venta,
    obtener_ventas_historial,
    obtener_detalle_venta,
    anular_venta,
    crear_cliente_rapido,
    buscar_cliente_por_dni,
    obtener_reporte_rendimiento
)

ventas_bp = Blueprint("ventas", __name__, url_prefix="/ventas")

@ventas_bp.route("/", methods=["GET"])
def index():
    medicamentos, clientes = listar_productos_y_clientes()
    ventas = obtener_ventas_historial()
    return render_template(
        "ventas.html",
        medicamentos=medicamentos,
        clientes=clientes,
        ventas=ventas
    )

@ventas_bp.route("/nueva", methods=["POST"])
def nueva():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Datos de venta no recibidos"}), 400
        
        id_cliente = data.get("id_cliente")
        metodo_pago = data.get("metodo_pago")
        productos = data.get("productos") # Espera una lista: [{"id_medicamento": X, "cantidad": Y}]
        
        if not id_cliente or not metodo_pago or not productos:
            return jsonify({"success": False, "message": "Faltan campos obligatorios"}), 400
        
        # En una aplicacion real se obtendria el id_usuario de la sesion.
        # Aqui inyectamos el ID de usuario 2 (Ana Gómez) o 1 (Juan Perez) como en el context processor de app.py
        id_usuario = 2 
        
        id_venta = registrar_venta(
            id_cliente=int(id_cliente),
            id_usuario=id_usuario,
            productos=productos,
            metodo_pago=metodo_pago
        )
        
        return jsonify({"success": True, "id_venta": id_venta, "message": "Venta registrada con exito"})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500

@ventas_bp.route("/<int:id_venta>/detalle", methods=["GET"])
def detalle(id_venta):
    data = obtener_detalle_venta(id_venta)
    if not data:
        return jsonify({"success": False, "message": "No se encontro la venta"}), 404
    return jsonify({"success": True, "data": data})

@ventas_bp.route("/<int:id_venta>/anular", methods=["POST"])
def anular(id_venta):
    try:
        anular_venta(id_venta)
        return redirect(url_for("ventas.index"))
    except Exception as e:
        # Podriamos pasar un mensaje flash de error
        return redirect(url_for("ventas.index"))

@ventas_bp.route("/clientes/buscar/<dni>", methods=["GET"])
def buscar_cliente(dni):
    try:
        dni_clean = dni.strip()
        if not dni_clean.isdigit() or len(dni_clean) != 8:
            return jsonify({"success": False, "message": "El DNI debe tener exactamente 8 dígitos numéricos"}), 400
            
        cliente = buscar_cliente_por_dni(dni_clean)
        if cliente:
            return jsonify({"success": True, "cliente": cliente})
        else:
            return jsonify({"success": False, "message": "Cliente no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@ventas_bp.route("/clientes/rapido", methods=["POST"])
def cliente_rapido():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        dni = data.get("dni", "").strip()
        telefono = data.get("telefono", "").strip()
        direccion = data.get("direccion", "").strip()
        
        if not nombre:
            return jsonify({"success": False, "message": "El nombre del cliente es obligatorio"}), 400
        if not dni:
            return jsonify({"success": False, "message": "El DNI del cliente es obligatorio"}), 400
        if not dni.isdigit() or len(dni) != 8:
            return jsonify({"success": False, "message": "El DNI debe tener exactamente 8 dígitos numéricos"}), 400
            
        # Verificar duplicado
        cliente_existente = buscar_cliente_por_dni(dni)
        if cliente_existente:
            return jsonify({"success": False, "message": "Ya existe un cliente registrado con este DNI"}), 400
            
        id_cliente = crear_cliente_rapido(nombre, dni, telefono, direccion)
        return jsonify({
            "success": True,
            "id_cliente": id_cliente,
            "nombre": nombre,
            "dni": dni,
            "message": "Cliente registrado correctamente"
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al registrar cliente: {str(e)}"}), 500

@ventas_bp.route("/reporte/exportar", methods=["GET"])
def exportar_reporte():
    try:
        min_ingreso_raw = request.args.get("min_ingreso", "15.00")
        try:
            min_ingreso = float(min_ingreso_raw)
        except ValueError:
            min_ingreso = 15.00
            
        reporte_data = obtener_reporte_rendimiento(min_ingreso)
        
        si = StringIO()
        si.write('\ufeff') # Añade el BOM UTF-8 para compatibilidad directa con Excel en Windows
        cw = csv.writer(si)
        
        # Escribir fila de cabecera
        cw.writerow([
            "ID Medicamento", 
            "Nombre Medicamento", 
            "Categoria", 
            "Total Unidades Vendidas", 
            "Ingresos Totales (S/)", 
            "Cantidad de Ventas"
        ])
        
        # Escribir filas de datos
        for row in reporte_data:
            cw.writerow([
                row["id_medicamento"],
                row["medicamento_nombre"],
                row["categoria_nombre"],
                row["total_unidades_vendidas"],
                f"{float(row['ingresos_totales']):.2f}",
                row["cantidad_ventas_realizadas"]
            ])
            
        response = Response(si.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename=reporte_rendimiento_min_{min_ingreso:.0f}.csv"
        return response
    except Exception as e:
        return f"Error al generar reporte: {str(e)}", 500

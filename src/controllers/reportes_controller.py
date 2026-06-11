from flask import Blueprint, render_template, request, make_response, Response, session
from src.database.connection import get_connection
import csv
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

reportes_bp = Blueprint('reportes', __name__)

# ─────────────────────────────────────────────
# QUERIES
# ─────────────────────────────────────────────

@reportes_bp.before_request
def verificar_permisos():
    
    if 'id_usuario' not in session:
        return redirect('/login')
    
    if session.get('rol') != 'Administrador':
        return "Acceso denegado. Esta sección es solo para el Administrador.", 403
    
def query_ventas_por_periodo(fecha_inicio, fecha_fin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            v.id_venta,
            v.fecha,
            c.nombre AS cliente,
            u.nombre AS usuario,
            v.total,
            p.metodo AS metodo_pago
        FROM VENTA v
        JOIN CLIENTE c ON v.id_cliente = c.id_cliente
        JOIN USUARIO u ON v.id_usuario = u.id_usuario
        LEFT JOIN PAGO p ON p.id_venta = v.id_venta
        WHERE v.fecha BETWEEN %s AND %s
        ORDER BY v.fecha DESC
    """, (fecha_inicio, fecha_fin))
    ventas = cursor.fetchall()

    cursor.execute("""
        SELECT
            m.nombre AS medicamento,
            SUM(dv.cantidad) AS total_vendido,
            SUM(dv.cantidad * dv.precio_unitario) AS ingreso_total
        FROM DETALLE_VENTA dv
        JOIN MEDICAMENTO m ON dv.id_medicamento = m.id_medicamento
        JOIN VENTA v ON dv.id_venta = v.id_venta
        WHERE v.fecha BETWEEN %s AND %s
        GROUP BY m.id_medicamento, m.nombre
        ORDER BY total_vendido DESC
    """, (fecha_inicio, fecha_fin))
    productos_top = cursor.fetchall()

    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) AS total_ingresos, COUNT(*) AS num_ventas
        FROM VENTA
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    resumen = cursor.fetchone()

    cursor.close()
    conn.close()
    return ventas, productos_top, resumen


def query_inventario():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            m.nombre AS medicamento,
            cat.nombre AS categoria,
            i.stock,
            i.stock_minimo,
            l.numero_lote,
            l.fecha_vencimiento,
            CASE
                WHEN i.stock <= i.stock_minimo THEN 'Stock bajo'
                WHEN l.fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL 90 DAY) THEN 'Próximo a vencer'
                ELSE 'OK'
            END AS estado
        FROM INVENTARIO i
        JOIN MEDICAMENTO m ON i.id_medicamento = m.id_medicamento AND m.activo = 1
        JOIN CATEGORIA cat ON m.id_categoria = cat.id_categoria
        JOIN LOTE l ON i.numero_lote = l.numero_lote AND i.id_medicamento = l.id_medicamento
        ORDER BY estado DESC, m.nombre
    """)
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT
            SUM(i.stock) AS total_unidades,
            COUNT(DISTINCT i.id_medicamento) AS tipos_medicamentos,
            SUM(CASE WHEN i.stock <= i.stock_minimo THEN 1 ELSE 0 END) AS con_stock_bajo,
            SUM(CASE WHEN l.fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL 90 DAY) THEN 1 ELSE 0 END) AS proximos_vencer
        FROM INVENTARIO i
        JOIN MEDICAMENTO m ON i.id_medicamento = m.id_medicamento AND m.activo = 1
        JOIN LOTE l ON i.numero_lote = l.numero_lote AND i.id_medicamento = l.id_medicamento
    """)
    resumen = cursor.fetchone()

    cursor.close()
    conn.close()
    return rows, resumen


def query_compras_por_proveedor(fecha_inicio, fecha_fin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            c.id_compra,
            c.fecha,
            p.nombre AS proveedor,
            u.nombre AS registrado_por,
            c.estado,
            COALESCE(SUM(dc.precio * dc.cantidad), 0) AS total_compra
        FROM COMPRA c
        JOIN PROVEEDOR p ON c.id_proveedor = p.id_proveedor
        JOIN USUARIO u ON c.id_usuario = u.id_usuario
        LEFT JOIN DETALLE_COMPRA dc ON dc.id_compra = c.id_compra
        WHERE c.fecha BETWEEN %s AND %s
        GROUP BY c.id_compra, c.fecha, p.nombre, u.nombre, c.estado
        ORDER BY c.fecha DESC
    """, (fecha_inicio, fecha_fin))
    compras = cursor.fetchall()

    cursor.execute("""
        SELECT
            p.nombre AS proveedor,
            COUNT(c.id_compra) AS num_compras,
            COALESCE(SUM(dc.precio * dc.cantidad), 0) AS total_invertido
        FROM COMPRA c
        JOIN PROVEEDOR p ON c.id_proveedor = p.id_proveedor
        LEFT JOIN DETALLE_COMPRA dc ON dc.id_compra = c.id_compra
        WHERE c.fecha BETWEEN %s AND %s
        GROUP BY p.id_proveedor, p.nombre
        ORDER BY total_invertido DESC
    """, (fecha_inicio, fecha_fin))
    por_proveedor = cursor.fetchall()

    cursor.close()
    conn.close()
    return compras, por_proveedor


# ─────────────────────────────────────────────
# RUTAS PRINCIPALES
# ─────────────────────────────────────────────

@reportes_bp.route('/reportes')
def index():
    return render_template('reportes/index.html')


@reportes_bp.route('/reportes/ventas')
def reporte_ventas():
    fecha_inicio = request.args.get('fecha_inicio', str(date.today().replace(day=1)))
    fecha_fin = request.args.get('fecha_fin', str(date.today()))
    ventas, productos_top, resumen = query_ventas_por_periodo(fecha_inicio, fecha_fin)
    return render_template('reportes/ventas.html',
                           ventas=ventas,
                           productos_top=productos_top,
                           resumen=resumen,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)


@reportes_bp.route('/reportes/inventario')
def reporte_inventario():
    inventario, resumen = query_inventario()
    return render_template('reportes/inventario.html',
                           inventario=inventario,
                           resumen=resumen)


@reportes_bp.route('/reportes/compras')
def reporte_compras():
    fecha_inicio = request.args.get('fecha_inicio', str(date.today().replace(day=1)))
    fecha_fin = request.args.get('fecha_fin', str(date.today()))
    compras, por_proveedor = query_compras_por_proveedor(fecha_inicio, fecha_fin)
    return render_template('reportes/compras.html',
                           compras=compras,
                           por_proveedor=por_proveedor,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)


# ─────────────────────────────────────────────
# EXPORTAR PDF
# ─────────────────────────────────────────────

def _pdf_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=16, alignment=TA_CENTER,
                                 fontName='Helvetica-Bold', spaceAfter=6)
    sub_style = ParagraphStyle('sub', fontSize=10, alignment=TA_CENTER,
                               fontName='Helvetica', spaceAfter=12, textColor=colors.grey)
    header_style = ParagraphStyle('header', fontSize=12, fontName='Helvetica-Bold',
                                  spaceBefore=12, spaceAfter=6)
    return title_style, sub_style, header_style


def _tabla_pdf(data, col_widths=None):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a6e3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7f3')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


@reportes_bp.route('/reportes/ventas/pdf')
def exportar_ventas_pdf():
    fecha_inicio = request.args.get('fecha_inicio', str(date.today().replace(day=1)))
    fecha_fin = request.args.get('fecha_fin', str(date.today()))
    ventas, productos_top, resumen = query_ventas_por_periodo(fecha_inicio, fecha_fin)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    title_s, sub_s, header_s = _pdf_styles()
    story = []

    story.append(Paragraph("SISFARMA-PERÚ", title_s))
    story.append(Paragraph(f"Reporte de Ventas | {fecha_inicio} al {fecha_fin}", sub_s))
    story.append(Spacer(1, 0.3*cm))

    # Resumen
    story.append(Paragraph("Resumen", header_s))
    resumen_data = [
        ['Total Ingresos', 'N° Ventas'],
        [f"S/ {resumen['total_ingresos']:.2f}", str(resumen['num_ventas'])]
    ]
    story.append(_tabla_pdf(resumen_data, col_widths=[9*cm, 9*cm]))
    story.append(Spacer(1, 0.4*cm))

    # Detalle de ventas
    story.append(Paragraph("Detalle de Ventas", header_s))
    ventas_data = [['ID', 'Fecha', 'Cliente', 'Atendido por', 'Método Pago', 'Total']]
    for v in ventas:
        ventas_data.append([
            str(v['id_venta']), str(v['fecha']), v['cliente'],
            v['usuario'], v['metodo_pago'] or '-', f"S/ {v['total']:.2f}"
        ])
    story.append(_tabla_pdf(ventas_data, col_widths=[1.5*cm, 2.5*cm, 4*cm, 4*cm, 3*cm, 3*cm]))
    story.append(Spacer(1, 0.4*cm))

    # Top productos
    story.append(Paragraph("Productos más vendidos", header_s))
    prod_data = [['Medicamento', 'Unidades Vendidas', 'Ingreso Total']]
    for p in productos_top:
        prod_data.append([p['medicamento'], str(p['total_vendido']), f"S/ {p['ingreso_total']:.2f}"])
    story.append(_tabla_pdf(prod_data, col_widths=[9*cm, 4.5*cm, 4.5*cm]))

    doc.build(story)
    buffer.seek(0)

    # Registrar en REPORTE (id_usuario=1 por defecto; ajustar con sesión si tienen login)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO REPORTE (tipo, fecha_generacion, id_usuario) VALUES (%s, %s, %s)",
                       ('ventas', str(date.today()), 1))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_ventas_{fecha_inicio}_{fecha_fin}.pdf'
    return response


@reportes_bp.route('/reportes/inventario/pdf')
def exportar_inventario_pdf():
    inventario, resumen = query_inventario()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    title_s, sub_s, header_s = _pdf_styles()
    story = []

    story.append(Paragraph("SISFARMA-PERÚ", title_s))
    story.append(Paragraph(f"Reporte de Inventario | {date.today()}", sub_s))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Resumen", header_s))
    res_data = [
        ['Total Unidades', 'Tipos Medicamentos', 'Stock Bajo', 'Próx. a Vencer'],
        [str(resumen['total_unidades']), str(resumen['tipos_medicamentos']),
         str(resumen['con_stock_bajo']), str(resumen['proximos_vencer'])]
    ]
    story.append(_tabla_pdf(res_data, col_widths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Detalle de Inventario", header_s))
    inv_data = [['Medicamento', 'Categoría', 'Lote', 'Stock', 'Mín.', 'Vencimiento', 'Estado']]
    for row in inventario:
        inv_data.append([
            row['medicamento'], row['categoria'], row['numero_lote'],
            str(row['stock']), str(row['stock_minimo']),
            str(row['fecha_vencimiento']), row['estado']
        ])
    story.append(_tabla_pdf(inv_data, col_widths=[4*cm, 3*cm, 2*cm, 1.5*cm, 1.5*cm, 3*cm, 3*cm]))

    doc.build(story)
    buffer.seek(0)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO REPORTE (tipo, fecha_generacion, id_usuario) VALUES (%s, %s, %s)",
                       ('inventario', str(date.today()), 1))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_inventario_{date.today()}.pdf'
    return response


@reportes_bp.route('/reportes/compras/pdf')
def exportar_compras_pdf():
    fecha_inicio = request.args.get('fecha_inicio', str(date.today().replace(day=1)))
    fecha_fin = request.args.get('fecha_fin', str(date.today()))
    compras, por_proveedor = query_compras_por_proveedor(fecha_inicio, fecha_fin)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    title_s, sub_s, header_s = _pdf_styles()
    story = []

    story.append(Paragraph("SISFARMA-PERÚ", title_s))
    story.append(Paragraph(f"Reporte de Compras | {fecha_inicio} al {fecha_fin}", sub_s))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Por Proveedor", header_s))
    prov_data = [['Proveedor', 'N° Compras', 'Total Invertido']]
    for p in por_proveedor:
        prov_data.append([p['proveedor'], str(p['num_compras']), f"S/ {p['total_invertido']:.2f}"])
    story.append(_tabla_pdf(prov_data, col_widths=[9*cm, 4.5*cm, 4.5*cm]))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Detalle de Compras", header_s))
    comp_data = [['ID', 'Fecha', 'Proveedor', 'Registrado por', 'Estado', 'Total']]
    for c in compras:
        comp_data.append([
            str(c['id_compra']), str(c['fecha']), c['proveedor'],
            c['registrado_por'], c['estado'], f"S/ {c['total_compra']:.2f}"
        ])
    story.append(_tabla_pdf(comp_data, col_widths=[1.5*cm, 2.5*cm, 4*cm, 3.5*cm, 2.5*cm, 4*cm]))

    doc.build(story)
    buffer.seek(0)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO REPORTE (tipo, fecha_generacion, id_usuario) VALUES (%s, %s, %s)",
                       ('compras', str(date.today()), 1))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_compras_{fecha_inicio}_{fecha_fin}.pdf'
    return response


# ─────────────────────────────────────────────
# EXPORTAR CSV
# ─────────────────────────────────────────────

@reportes_bp.route('/reportes/inventario/csv')
def exportar_inventario_csv():
    inventario, _ = query_inventario()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Medicamento', 'Categoría', 'Lote', 'Stock', 'Stock Mínimo', 'Vencimiento', 'Estado'])
    for row in inventario:
        writer.writerow([row['medicamento'], row['categoria'], row['numero_lote'],
                         row['stock'], row['stock_minimo'], row['fecha_vencimiento'], row['estado']])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename=inventario_{date.today()}.csv'})


@reportes_bp.route('/reportes/ventas/csv')
def exportar_ventas_csv():
    fecha_inicio = request.args.get('fecha_inicio', str(date.today().replace(day=1)))
    fecha_fin = request.args.get('fecha_fin', str(date.today()))
    ventas, _, _ = query_ventas_por_periodo(fecha_inicio, fecha_fin)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Fecha', 'Cliente', 'Atendido por', 'Método Pago', 'Total'])
    for v in ventas:
        writer.writerow([v['id_venta'], v['fecha'], v['cliente'],
                         v['usuario'], v['metodo_pago'] or '-', v['total']])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename=ventas_{fecha_inicio}_{fecha_fin}.csv'})

@reportes_bp.route('/reportes/compras/csv')
def exportar_compras_csv():
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    conn = get_connection()
    cursor = conn.cursor() 
    

    query = """
        SELECT 
            c.id_compra,
            c.fecha,
            p.nombre AS proveedor,
            m.nombre AS medicamento,
            dc.cantidad,
            dc.precio AS precio_unitario,
            (dc.cantidad * dc.precio) AS total_item,
            c.estado
        FROM COMPRA c
        JOIN PROVEEDOR p ON c.id_proveedor = p.id_proveedor
        JOIN DETALLE_COMPRA dc ON c.id_compra = dc.id_compra
        JOIN MEDICAMENTO m ON dc.id_medicamento = m.id_medicamento
        WHERE (%s = '' OR c.fecha >= %s) AND (%s = '' OR c.fecha <= %s)
        ORDER BY c.fecha DESC, c.id_compra DESC;
    """
    
    cursor.execute(query, (fecha_inicio, fecha_inicio, fecha_fin, fecha_fin))
    compras_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    

    writer.writerow([
        'ID Compra', 'Fecha', 'Proveedor', 'Medicamento', 
        'Cantidad', 'Precio Unitario (S/)', 'Total (S/)', 'Estado'
    ])
    
    for row in compras_data:

        if isinstance(row, dict):
            id_c = row.get('id_compra')
            fec = row.get('fecha')
            prov = row.get('proveedor')
            med = row.get('medicamento')
            cant = row.get('cantidad', 0)
            p_uni = row.get('precio_unitario', 0.0)
            tot = row.get('total_item', 0.0)
            est = row.get('estado', 'pendiente')
        else:
            id_c = row[0]
            fec = row[1]
            prov = row[2]
            med = row[3]
            cant = row[4]
            p_uni = row[5]
            tot = row[6]
            est = row[7]
            
        writer.writerow([
            f"#OC-{id_c:04d}" if isinstance(id_c, int) else id_c,
            fec,
            prov,
            med,
            cant,
            f"{float(p_uni):.2f}",
            f"{float(tot):.2f}",
            str(est).upper()
        ])
        
    output.seek(0)
    return Response(
        output.getvalue(), 
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=reporte_compras_{date.today()}.csv'}
    )
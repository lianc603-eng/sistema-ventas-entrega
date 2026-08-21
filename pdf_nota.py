from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def hex_a_color(hex_str: str, default="#000000"):
    try:
        hex_clean = hex_str.lstrip("#")
        if len(hex_clean) == 6:
            r = int(hex_clean[0:2], 16) / 255.0
            g = int(hex_clean[2:4], 16) / 255.0
            b = int(hex_clean[4:6], 16) / 255.0
            return colors.Color(r, g, b)
    except Exception:
        pass
    return colors.HexColor(default)

def generar_nota_pdf(cabecera: dict, partidas: list, config_personalizada: dict = None):
    cfg = config_personalizada or {}
    
    # Fuentes y Textos
    fuente_familia = cfg.get("fuente_familia", "Helvetica")
    fuente_bold = f"{fuente_familia}-Bold" if fuente_familia in ["Helvetica", "Times-Roman", "Courier"] else "Helvetica-Bold"
    
    titulo_doc = cfg.get("titulo_documento", "COMPROBANTE DE PAGO")
    subtitulo_doc = cfg.get("subtitulo_documento", "Servicios Profesionales")
    nombre_negocio = cfg.get("nombre_negocio", "Mi Negocio")
    contacto_negocio = cfg.get("contacto_negocio", "981 000 0000")
    mensaje_pie = cfg.get("mensaje_pie", "Gracias por su preferencia.")
    lbl_fecha = cfg.get("etiqueta_fecha_operativa", "Fecha:")
    lbl_lugar = cfg.get("etiqueta_lugar_operativo", "Lugar:")
    lbl_detalle = cfg.get("etiqueta_detalle", "Descripción")
    firma_izq = cfg.get("firma_izquierda", "Entregado por")
    firma_der = cfg.get("firma_derecha", "Recibido de Conformidad")
    simbolo_moneda = cfg.get("moneda", "$")
    
    # Colores
    col_acento = hex_a_color(cfg.get("color_primario", "#E11D48"))
    col_tabla = hex_a_color(cfg.get("color_tabla_fondo", "#881337"))
    col_txt_tabla = hex_a_color(cfg.get("color_tabla_texto", "#FFFFFF"))
    
    # Opciones
    mostrar_firmas = cfg.get("mostrar_firmas", True)
    desglosar_iva = cfg.get("desglosar_iva", False)
    tasa_iva = float(cfg.get("tasa_iva", 16.0))
    logo_bytes = cfg.get("logo_bytes", None)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    st_titulo = ParagraphStyle("TitDoc", parent=styles["Normal"], fontName=fuente_bold, fontSize=15, textColor=col_acento, leading=18, alignment=TA_LEFT)
    st_sub = ParagraphStyle("SubDoc", parent=styles["Normal"], fontName=fuente_familia, fontSize=9, textColor=colors.HexColor("#475569"), leading=12, alignment=TA_LEFT)
    st_negocio = ParagraphStyle("NegDoc", parent=styles["Normal"], fontName=fuente_bold, fontSize=13, textColor=colors.HexColor("#0F172A"), leading=15, alignment=TA_RIGHT)
    st_contacto = ParagraphStyle("ContDoc", parent=styles["Normal"], fontName=fuente_familia, fontSize=9, textColor=colors.HexColor("#64748B"), leading=12, alignment=TA_RIGHT)
    st_cell = ParagraphStyle("Cell", parent=styles["Normal"], fontName=fuente_familia, fontSize=9, leading=11)
    st_cell_h = ParagraphStyle("CellH", parent=styles["Normal"], fontName=fuente_bold, fontSize=9, textColor=col_txt_tabla, leading=11, alignment=TA_CENTER)

    story = []

    # ENCABEZADO CON LOGO O TEXTO
    logo_elem = None
    if logo_bytes:
        try:
            img_io = BytesIO(logo_bytes)
            logo_elem = RLImage(img_io, width=80, height=50)
        except Exception:
            logo_elem = None

    if logo_elem:
        fila_h = [
            logo_elem,
            [Paragraph(titulo_doc, st_titulo), Paragraph(subtitulo_doc, st_sub)],
            [Paragraph(nombre_negocio, st_negocio), Paragraph(f"WhatsApp: {contacto_negocio}", st_contacto)]
        ]
        t_head = Table([fila_h], colWidths=[90, 260, 190])
    else:
        fila_h = [
            [Paragraph(titulo_doc, st_titulo), Paragraph(subtitulo_doc, st_sub)],
            [Paragraph(nombre_negocio, st_negocio), Paragraph(f"WhatsApp: {contacto_negocio}", st_contacto)]
        ]
        t_head = Table([fila_h], colWidths=[340, 200])

    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_head)
    story.append(Spacer(1, 12))

    # BLOQUE DE DATOS GENERALES
    datos_cliente = [
        [
            Paragraph(f"<b>Folio:</b> {cabecera.get('folio', 'N/A')}", st_cell),
            Paragraph(f"<b>{lbl_fecha}</b> {cabecera.get('fecha_entrega', '')}", st_cell)
        ],
        [
            Paragraph(f"<b>Cliente:</b> {cabecera.get('cliente', 'Mostrador')}", st_cell),
            Paragraph(f"<b>WhatsApp:</b> {cabecera.get('telefono', 'S/N')}", st_cell)
        ],
        [
            Paragraph(f"<b>{lbl_lugar}</b> {cabecera.get('direccion', 'Mostrador')}", st_cell),
            Paragraph(f"<b>Emisión:</b> {cabecera.get('fecha_registro', '')}", st_cell)
        ]
    ]
    t_cli = Table(datos_cliente, colWidths=[320, 220])
    t_cli.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 14))

    # TABLA DE CONCEPTOS
    tabla_data = [[
        Paragraph(lbl_detalle, st_cell_h),
        Paragraph("Cant.", st_cell_h),
        Paragraph(f"P. Unit ({simbolo_moneda})", st_cell_h),
        Paragraph(f"Subtotal ({simbolo_moneda})", st_cell_h)
    ]]

    for p in partidas:
        tabla_data.append([
            Paragraph(str(p.get("producto", "")), st_cell),
            Paragraph(str(p.get("cantidad", 1)), st_cell),
            Paragraph(f"{float(p.get('precio_unitario', 0)):,.2f}", st_cell),
            Paragraph(f"{float(p.get('subtotal', 0)):,.2f}", st_cell)
        ])

    t_partidas = Table(tabla_data, colWidths=[280, 50, 100, 110])
    t_partidas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), col_tabla),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_partidas)
    story.append(Spacer(1, 10))

    # TOTALES Y DESGLOSE DE IVA
    total_num = float(cabecera.get("total", 0.0))
    anticipo_num = float(cabecera.get("anticipo", 0.0))
    saldo_num = float(cabecera.get("saldo", 0.0))

    totales_data = []
    if desglosar_iva:
        subtotal_base = total_num / (1 + (tasa_iva / 100))
        monto_iva = total_num - subtotal_base
        totales_data.append([Paragraph(f"Subtotal:", st_cell), Paragraph(f"{simbolo_moneda}{subtotal_base:,.2f}", st_cell)])
        totales_data.append([Paragraph(f"IVA ({tasa_iva:g}%):", st_cell), Paragraph(f"{simbolo_moneda}{monto_iva:,.2f}", st_cell)])
        
    totales_data.append([Paragraph(f"<b>TOTAL:</b>", st_cell), Paragraph(f"<b>{simbolo_moneda}{total_num:,.2f}</b>", st_cell)])
    totales_data.append([Paragraph(f"Anticipo:", st_cell), Paragraph(f"{simbolo_moneda}{anticipo_num:,.2f}", st_cell)])
    totales_data.append([Paragraph(f"<b>SALDO PENDIENTE:</b>", st_cell), Paragraph(f"<b>{simbolo_moneda}{saldo_num:,.2f}</b>", st_cell)])

    t_tot = Table(totales_data, colWidths=[130, 90])
    t_tot.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('BOX', (0,0), (-1,-1), 1, col_acento),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    t_pie = Table([
        [Paragraph(f"<i>{mensaje_pie}</i>", ParagraphStyle("PieMsg", parent=styles["Normal"], fontName=fuente_familia, fontSize=8, textColor=colors.HexColor("#64748B"))), t_tot]
    ], colWidths=[310, 230])
    t_pie.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_pie)

    # FIRMAS
    if mostrar_firmas:
        story.append(Spacer(1, 25))
        t_firmas = Table([
            [Paragraph("________________________________", st_cell), Paragraph("________________________________", st_cell)],
            [Paragraph(f"<b>{firma_izq}</b>", st_cell), Paragraph(f"<b>{firma_der}</b>", st_cell)]
        ], colWidths=[270, 270])
        t_firmas.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(t_firmas)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

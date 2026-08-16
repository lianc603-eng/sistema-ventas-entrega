from fpdf import FPDF
import io

def hex_to_rgb(hex_str: str):
    """Convierte color hexadecimal (#RRGGBB) a tupla (R, G, B)."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

class NotaEntregaPDF(FPDF):
    def __init__(self, config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    def header(self):
        # Color de fondo de toda la hoja
        r_bg, g_bg, b_bg = hex_to_rgb(self.config.get("color_fondo_hoja", "#FFFFFF"))
        self.set_fill_color(r_bg, g_bg, b_bg)
        self.rect(0, 0, 216, 279, 'F')

        # Franja decorativa superior
        r_p, g_p, b_p = hex_to_rgb(self.config.get("color_primario", "#10B981"))
        self.set_fill_color(r_p, g_p, b_p)
        self.rect(0, 0, 216, 6, 'F')
        
        # Logo opcional
        logo_bytes = self.config.get("logo_bytes")
        start_x = 14
        if logo_bytes:
            try:
                self.image(io.BytesIO(logo_bytes), x=14, y=10, h=15)
                start_x = 42
            except Exception:
                pass
        
        self.set_xy(start_x, 11)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(15, 23, 42)
        titulo_doc = self.config.get("titulo_documento", "NOTA DE VENTA Y REMISIÓN")
        self.cell(100, 6, titulo_doc, ln=False)
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 116, 139)
        subtitulo_doc = self.config.get("subtitulo_documento", "Comprobante de Entrega y Despacho")
        self.cell(88 if not logo_bytes else (202 - start_x - 100), 6, subtitulo_doc, ln=True, align='R')
        
        negocio = self.config.get("nombre_negocio", "")
        contacto = self.config.get("contacto_negocio", "")
        if negocio or contacto:
            self.set_xy(start_x, 17)
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(71, 85, 105)
            self.cell(100, 4, negocio, ln=False)
            self.set_font('Helvetica', '', 8)
            self.cell(88 if not logo_bytes else (202 - start_x - 100), 4, contacto, ln=True, align='R')

        self.ln(4)

    def footer(self):
        self.set_y(-18)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        pie_pagina = self.config.get("mensaje_pie", "Favor de revisar el producto al momento de su entrega.")
        self.cell(0, 4, pie_pagina, align='C', ln=True)
        self.cell(0, 4, f'Página {self.page_no()}/{{nb}}', align='C')

def generar_nota_pdf(cabecera: dict, partidas: list, config_personalizada: dict = None) -> bytes:
    config = {
        "titulo_documento": "NOTA DE VENTA Y REMISIÓN",
        "subtitulo_documento": "Comprobante de Entrega y Despacho",
        "nombre_negocio": "",
        "contacto_negocio": "",
        "mensaje_pie": "Favor de revisar el producto al momento de su entrega.",
        "firma_izquierda": "Entregado por (Vendedor/Repartidor)",
        "firma_derecha": "Firma de Recibido de Conformidad (Cliente)",
        "color_fondo_hoja": "#FFFFFF",
        "color_primario": "#10B981",
        "color_tabla_fondo": "#1E293B",
        "color_tabla_texto": "#FFFFFF",
        "mostrar_firmas": True,
        "logo_bytes": None
    }
    if config_personalizada:
        config.update(config_personalizada)

    pdf = NotaEntregaPDF(config=config, orientation='P', unit='mm', format='Letter')
    pdf.alias_nb_pages()
    pdf.add_page()

    r_p, g_p, b_p = hex_to_rgb(config["color_primario"])

    # Tarjeta de Datos de la Venta
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(14, 25, 188, 32, 'FD')

    # Fila 1
    pdf.set_xy(18, 28)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Folio:', border=0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, str(cabecera.get('folio', '')), border=0)

    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(r_p, g_p, b_p)
    pdf.cell(32, 5, 'DÍA DE ENTREGA:', border=0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, str(cabecera.get('fecha_entrega', '')), border=0, ln=True)

    # Fila 2
    pdf.set_x(18)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Cliente:', border=0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, str(cabecera.get('cliente', '')), border=0)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(32, 5, 'Horario acordado:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, str(cabecera.get('horario_entrega', 'Horario abierto')), border=0, ln=True)

    # Fila 3
    pdf.set_x(18)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Teléfono:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, str(cabecera.get('telefono', '')), border=0)

    pdf.set_text_color(71, 85, 105)
    pdf.cell(32, 5, 'Lugar de entrega:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, str(cabecera.get('direccion', 'Mostrador'))[:30], border=0, ln=True)

    pdf.ln(8)

    # Tabla de Productos
    r_tf, g_tf, b_tf = hex_to_rgb(config["color_tabla_fondo"])
    r_tt, g_tt, b_tt = hex_to_rgb(config["color_tabla_texto"])
    
    pdf.set_x(14)
    pdf.set_fill_color(r_tf, g_tf, b_tf)
    pdf.set_text_color(r_tt, g_tt, b_tt)
    pdf.set_font('Helvetica', 'B', 9)

    pdf.cell(100, 7, ' Descripción del Producto / Artículo', border=0, fill=True)
    pdf.cell(24, 7, 'Cant.', border=0, align='C', fill=True)
    pdf.cell(32, 7, 'P. Unitario', border=0, align='R', fill=True)
    pdf.cell(32, 7, 'Subtotal', border=0, align='R', fill=True)
    pdf.ln()

    # Partidas
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(30, 41, 59)
    fill = False
    for item in partidas:
        pdf.set_x(14)
        pdf.set_fill_color(248, 250, 252) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(100, 6.5, f" {item.get('producto', '')}", border='B', fill=True)
        pdf.cell(24, 6.5, str(item.get('cantidad', 1)), border='B', align='C', fill=True)
        pdf.cell(32, 6.5, f"${float(item.get('precio_unitario', 0)):,.2f}", border='B', align='R', fill=True)
        pdf.cell(32, 6.5, f"${float(item.get('subtotal', 0)):,.2f}", border='B', align='R', fill=True)
        pdf.ln()
        fill = not fill

    # Resumen Financiero
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 9.5)

    pdf.set_x(14)
    pdf.cell(124, 5.5, '', border=0)
    pdf.cell(32, 5.5, 'Total Venta:', border=0, align='R')
    pdf.cell(32, 5.5, f"${float(cabecera.get('total', 0)):,.2f}", border=0, align='R')
    pdf.ln()

    pdf.set_x(14)
    pdf.cell(124, 5.5, '', border=0)
    pdf.cell(32, 5.5, 'Anticipo Pagado:', border=0, align='R')
    pdf.cell(32, 5.5, f"${float(cabecera.get('anticipo', 0)):,.2f}", border=0, align='R')
    pdf.ln()

    saldo = float(cabecera.get('saldo', 0))
    pdf.set_x(14)
    pdf.set_fill_color(254, 242, 242) if saldo > 0 else pdf.set_fill_color(240, 253, 244)
    pdf.set_text_color(220, 38, 38) if saldo > 0 else pdf.set_text_color(22, 101, 52)
    pdf.cell(124, 7, '', border=0)
    pdf.cell(32, 7, 'SALDO A COBRAR:', border=1, align='R', fill=True)
    pdf.cell(32, 7, f"${saldo:,.2f}", border=1, align='R', fill=True)
    pdf.ln(16)

    # Firmas
    if config.get("mostrar_firmas", True):
        pdf.set_text_color(71, 85, 105)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_x(14)
        pdf.cell(85, 4, '__________________________________', align='C')
        pdf.cell(18, 4, '')
        pdf.cell(85, 4, '__________________________________', align='C', ln=True)

        pdf.set_x(14)
        pdf.cell(85, 4, config.get("firma_izquierda", "Entregado por"), align='C')
        pdf.cell(18, 4, '')
        pdf.cell(85, 4, config.get("firma_derecha", "Recibido de Conformidad"), align='C', ln=True)

    return bytes(pdf.output())

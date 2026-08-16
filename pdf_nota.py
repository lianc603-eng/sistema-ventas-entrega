from fpdf import FPDF
import io

def hex_to_rgb(hex_str: str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

class NotaUniversalPDF(FPDF):
    def __init__(self, config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    def header(self):
        # Color de fondo de la hoja completa
        r_bg, g_bg, b_bg = hex_to_rgb(self.config.get("color_fondo_hoja", "#FFFFFF"))
        self.set_fill_color(r_bg, g_bg, b_bg)
        self.rect(0, 0, 216, 279, 'F')

        # Franja decorativa de color de acento
        r_p, g_p, b_p = hex_to_rgb(self.config.get("color_primario", "#2563EB"))
        self.set_fill_color(r_p, g_p, b_p)
        self.rect(0, 0, 216, 6, 'F')
        
        # Inserción de Logo si existe
        logo_bytes = self.config.get("logo_bytes")
        start_x = 14
        if logo_bytes:
            try:
                self.image(io.BytesIO(logo_bytes), x=14, y=10, h=16)
                start_x = 46
            except Exception:
                pass
        
        self.set_xy(start_x, 11)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(15, 23, 42)
        self.cell(105, 6, self.config.get("titulo_documento", "COMPROBANTE COMERCIAL"), ln=False)
        
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(100, 116, 139)
        self.cell(202 - start_x - 105, 6, self.config.get("subtitulo_documento", "Documento de Control"), ln=True, align='R')
        
        negocio = self.config.get("nombre_negocio", "")
        contacto = self.config.get("contacto_negocio", "")
        if negocio or contacto:
            self.set_xy(start_x, 17)
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(71, 85, 105)
            self.cell(105, 4, negocio, ln=False)
            self.set_font('Helvetica', '', 8)
            self.cell(202 - start_x - 105, 4, contacto, ln=True, align='R')

        self.ln(4)

    def footer(self):
        self.set_y(-18)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 4, self.config.get("mensaje_pie", "Gracias por su preferencia."), align='C', ln=True)
        self.cell(0, 4, f'Página {self.page_no()}/{{nb}}', align='C')

def generar_nota_pdf(cabecera: dict, partidas: list, config_personalizada: dict = None) -> bytes:
    config = {
        "titulo_documento": "COMPROBANTE COMERCIAL",
        "subtitulo_documento": "Orden de Servicio / Venta",
        "nombre_negocio": "",
        "contacto_negocio": "",
        "mensaje_pie": "Gracias por su preferencia.",
        "etiqueta_fecha_operativa": "FECHA DE ENTREGA / SERVICIO:",
        "etiqueta_lugar_operativo": "Lugar / Ubicación:",
        "etiqueta_detalle": "Descripción del Concepto / Artículo",
        "firma_izquierda": "Emitido por (Responsable)",
        "firma_derecha": "Conformidad del Cliente",
        "moneda": "$",
        "color_fondo_hoja": "#FFFFFF",
        "color_primario": "#2563EB",
        "color_tabla_fondo": "#0F172A",
        "color_tabla_texto": "#FFFFFF",
        "mostrar_firmas": True,
        "desglosar_iva": False,
        "tasa_iva": 16.0,
        "logo_bytes": None
    }
    if config_personalizada:
        config.update(config_personalizada)

    pdf = NotaUniversalPDF(config=config, orientation='P', unit='mm', format='Letter')
    pdf.alias_nb_pages()
    pdf.add_page()

    r_p, g_p, b_p = hex_to_rgb(config["color_primario"])
    simbolo = config.get("moneda", "$")

    # Tarjeta de Datos Generales
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(14, 25, 188, 32, 'FD')

    # Fila 1
    pdf.set_xy(18, 28)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Folio / ID:', border=0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, str(cabecera.get('folio', '')), border=0)

    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(r_p, g_p, b_p)
    pdf.cell(42, 5, config.get("etiqueta_fecha_operativa", "FECHA:"), border=0)
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(40, 5, str(cabecera.get('fecha_entrega', '')), border=0, ln=True)

    # Fila 2
    pdf.set_x(18)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Cliente / Titular:', border=0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, str(cabecera.get('cliente', ''))[:30], border=0)

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(42, 5, 'Horario / Turno:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(40, 5, str(cabecera.get('horario_entrega', 'N/A')), border=0, ln=True)

    # Fila 3
    pdf.set_x(18)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Contacto / Tel:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, str(cabecera.get('telefono', 'S/N')), border=0)

    pdf.set_text_color(71, 85, 105)
    pdf.cell(42, 5, config.get("etiqueta_lugar_operativo", "Lugar / Ubicación:"), border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(40, 5, str(cabecera.get('direccion', 'Mostrador'))[:25], border=0, ln=True)

    pdf.ln(8)

    # Encabezado de la Tabla
    r_tf, g_tf, b_tf = hex_to_rgb(config["color_tabla_fondo"])
    r_tt, g_tt, b_tt = hex_to_rgb(config["color_tabla_texto"])
    
    pdf.set_x(14)
    pdf.set_fill_color(r_tf, g_tf, b_tf)
    pdf.set_text_color(r_tt, g_tt, b_tt)
    pdf.set_font('Helvetica', 'B', 8.5)

    etiqueta_concepto = f" {config.get('etiqueta_detalle', 'Descripción / Concepto')}"
    pdf.cell(100, 7, etiqueta_concepto[:40], border=0, fill=True)
    pdf.cell(24, 7, 'Cant.', border=0, align='C', fill=True)
    pdf.cell(32, 7, f'P. Unit ({simbolo})', border=0, align='R', fill=True)
    pdf.cell(32, 7, f'Importe ({simbolo})', border=0, align='R', fill=True)
    pdf.ln()

    # Partidas
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(30, 41, 59)
    fill = False
    for item in partidas:
        pdf.set_x(14)
        pdf.set_fill_color(248, 250, 252) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(100, 6.5, f" {item.get('producto', '')}", border='B', fill=True)
        pdf.cell(24, 6.5, str(item.get('cantidad', 1)), border='B', align='C', fill=True)
        pdf.cell(32, 6.5, f"{simbolo}{float(item.get('precio_unitario', 0)):,.2f}", border='B', align='R', fill=True)
        pdf.cell(32, 6.5, f"{simbolo}{float(item.get('subtotal', 0)):,.2f}", border='B', align='R', fill=True)
        pdf.ln()
        fill = not fill

    # Resumen Financiero y Desglose de IVA
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 9)
    total_base = float(cabecera.get('total', 0))
    anticipo = float(cabecera.get('anticipo', 0))

    if config.get("desglosar_iva", False):
        tasa = float(config.get("tasa_iva", 16.0))
        subtotal_neto = total_base / (1 + (tasa / 100))
        iva_calculado = total_base - subtotal_neto

        pdf.set_x(14)
        pdf.cell(124, 4.5, '', border=0)
        pdf.cell(32, 4.5, 'Subtotal Neto:', border=0, align='R')
        pdf.cell(32, 4.5, f"{simbolo}{subtotal_neto:,.2f}", border=0, align='R', ln=True)

        pdf.set_x(14)
        pdf.cell(124, 4.5, '', border=0)
        pdf.cell(32, 4.5, f'IVA ({tasa:g}%):', border=0, align='R')
        pdf.cell(32, 4.5, f"{simbolo}{iva_calculado:,.2f}", border=0, align='R', ln=True)

    pdf.set_x(14)
    pdf.cell(124, 5, '', border=0)
    pdf.cell(32, 5, 'Total:', border=0, align='R')
    pdf.cell(32, 5, f"{simbolo}{total_base:,.2f}", border=0, align='R', ln=True)

    if anticipo > 0:
        pdf.set_x(14)
        pdf.cell(124, 5, '', border=0)
        pdf.cell(32, 5, 'Anticipo / Adelanto:', border=0, align='R')
        pdf.cell(32, 5, f"{simbolo}{anticipo:,.2f}", border=0, align='R', ln=True)

    saldo = float(cabecera.get('saldo', 0))
    pdf.set_x(14)
    pdf.set_fill_color(254, 242, 242) if saldo > 0 else pdf.set_fill_color(240, 253, 244)
    pdf.set_text_color(220, 38, 38) if saldo > 0 else pdf.set_text_color(22, 101, 52)
    pdf.cell(124, 6.5, '', border=0)
    pdf.cell(32, 6.5, 'SALDO A LIQUIDAR:', border=1, align='R', fill=True)
    pdf.cell(32, 6.5, f"{simbolo}{saldo:,.2f}", border=1, align='R', fill=True)
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
        pdf.cell(85, 4, config.get("firma_izquierda", "Emitido por"), align='C')
        pdf.cell(18, 4, '')
        pdf.cell(85, 4, config.get("firma_derecha", "Recibido de Conformidad"), align='C', ln=True)

    return bytes(pdf.output())

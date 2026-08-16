from fpdf import FPDF

class NotaEntregaPDF(FPDF):
    def header(self):
        # Franja decorativa
        self.set_fill_color(16, 185, 129) # Emerald Green
        self.rect(0, 0, 216, 6, 'F')
        
        self.set_xy(14, 12)
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(15, 23, 42)
        self.cell(100, 6, 'NOTA DE VENTA Y REMISIÓN', ln=False)
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 116, 139)
        self.cell(88, 6, 'Comprobante de Entrega y Despacho', ln=True, align='R')
        self.ln(4)

    def footer(self):
        self.set_y(-18)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 4, 'Favor de revisar el producto al momento de su entrega.', align='C', ln=True)
        self.cell(0, 4, f'Página {self.page_no()}/{{nb}}', align='C')

def generar_nota_pdf(cabecera: dict, partidas: list) -> bytes:
    pdf = NotaEntregaPDF(orientation='P', unit='mm', format='Letter')
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- Bloque Datos de la Venta y Entrega ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(14, 24, 188, 32, 'FD')

    # Fila 1
    pdf.set_xy(18, 27)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Folio:', border=0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, cabecera['folio'], border=0)

    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(32, 5, 'DÍA DE ENTREGA:', border=0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, cabecera['fecha_entrega'], border=0, ln=True)

    # Fila 2
    pdf.set_x(18)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Cliente:', border=0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, cabecera['cliente'], border=0)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(32, 5, 'Horario acordado:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, cabecera.get('horario_entrega', 'Horario abierto'), border=0, ln=True)

    # Fila 3
    pdf.set_x(18)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(24, 5, 'Teléfono:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(66, 5, cabecera['telefono'], border=0)

    pdf.set_text_color(71, 85, 105)
    pdf.cell(32, 5, 'Lugar de entrega:', border=0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, cabecera.get('direccion', 'Mostrador')[:30], border=0, ln=True)

    pdf.ln(8)

    # --- Tabla de Desglose de Productos ---
    pdf.set_x(14)
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)

    pdf.cell(100, 7, ' Descripción del Producto / Artículo', border=0, fill=True)
    pdf.cell(24, 7, 'Cant.', border=0, align='C', fill=True)
    pdf.cell(32, 7, 'P. Unitario', border=0, align='R', fill=True)
    pdf.cell(32, 7, 'Subtotal', border=0, align='R', fill=True)
    pdf.ln()

    # Filas
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(30, 41, 59)
    fill = False
    for item in partidas:
        pdf.set_x(14)
        pdf.set_fill_color(248, 250, 252) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(100, 6.5, f" {item['producto']}", border='B', fill=True)
        pdf.cell(24, 6.5, str(item['cantidad']), border='B', align='C', fill=True)
        pdf.cell(32, 6.5, f"${item['precio_unitario']:,.2f}", border='B', align='R', fill=True)
        pdf.cell(32, 6.5, f"${item['subtotal']:,.2f}", border='B', align='R', fill=True)
        pdf.ln()
        fill = not fill

    # --- Resumen Financiero ---
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 9.5)

    pdf.set_x(14)
    pdf.cell(124, 5.5, '', border=0)
    pdf.cell(32, 5.5, 'Total Venta:', border=0, align='R')
    pdf.cell(32, 5.5, f"${cabecera['total']:,.2f}", border=0, align='R')
    pdf.ln()

    pdf.set_x(14)
    pdf.cell(124, 5.5, '', border=0)
    pdf.cell(32, 5.5, 'Anticipo Pagado:', border=0, align='R')
    pdf.cell(32, 5.5, f"${cabecera['anticipo']:,.2f}", border=0, align='R')
    pdf.ln()

    pdf.set_x(14)
    pdf.set_fill_color(254, 242, 242) if cabecera['saldo'] > 0 else pdf.set_fill_color(240, 253, 244)
    pdf.set_text_color(220, 38, 38) if cabecera['saldo'] > 0 else pdf.set_text_color(22, 101, 52)
    pdf.cell(124, 7, '', border=0)
    pdf.cell(32, 7, 'SALDO A COBRAR:', border=1, align='R', fill=True)
    pdf.cell(32, 7, f"${cabecera['saldo']:,.2f}", border=1, align='R', fill=True)
    pdf.ln(18)

    # --- Firmas de Conformidad ---
    pdf.set_text_color(71, 85, 105)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_x(14)
    pdf.cell(85, 4, '__________________________________', align='C')
    pdf.cell(18, 4, '')
    pdf.cell(85, 4, '__________________________________', align='C', ln=True)

    pdf.set_x(14)
    pdf.cell(85, 4, 'Entregado por (Vendedor/Repartidor)', align='C')
    pdf.cell(18, 4, '')
    pdf.cell(85, 4, 'Firma de Recibido de Conformidad (Cliente)', align='C', ln=True)

    return bytes(pdf.output())

import streamlit as st
import datetime
import uuid
import db
import pdf_nota

st.set_page_config(page_title="Gestor Comercial Universal & Comprobantes", layout="wide", page_icon="💼")
db.init_db()

if "partidas_actuales" not in st.session_state:
    st.session_state.partidas_actuales = []
if "ultima_venta" not in st.session_state:
    st.session_state.ultima_venta = None

# =========================================================
# PRESETS DE GIROS DE NEGOCIOS PARA MONETIZACIÓN
# =========================================================
PRESETS_GIROS = {
    "Comercio General / Entregas": {
        "titulo": "NOTA DE VENTA Y REMISIÓN",
        "subtitulo": "Comprobante de Entrega y Despacho",
        "etiqueta_fecha": "FECHA DE ENTREGA:",
        "etiqueta_lugar": "Lugar / Dirección de Entrega:",
        "etiqueta_detalle": "Descripción del Artículo / Producto",
        "firma_izq": "Entregado por (Vendedor/Repartidor)",
        "firma_der": "Recibido de Conformidad (Cliente)",
        "color_primario": "#10B981",
        "color_tabla": "#0F172A",
        "placeholder_prod": "Ej: Producto A, Caja de refacciones..."
    },
    "Renta de Mobiliario y Eventos": {
        "titulo": "CONTRATO Y NOTA DE RENTA DE MOBILIARIO",
        "subtitulo": "Orden de Servicio para Eventos",
        "etiqueta_fecha": "FECHA DEL EVENTO / MONTAJE:",
        "etiqueta_lugar": "Dirección del Evento / Salón:",
        "etiqueta_detalle": "Mobiliario / Equipo en Renta",
        "firma_izq": "Entregado por (Coordinador / Chofer)",
        "firma_der": "Aceptación de Mobiliario y Condiciones",
        "color_primario": "#6366F1",
        "color_tabla": "#1E1B4B",
        "placeholder_prod": "Ej: Juego de Mesa Redonda + 10 Sillas Tiffany"
    },
    "Agencia Digital / Fotografía / Producción": {
        "titulo": "COTIZACIÓN Y ORDEN DE SERVICIO",
        "subtitulo": "Servicios Creativos, Marketing y Cobertura",
        "etiqueta_fecha": "FECHA DE SESIÓN / ENTREGA DIGITAL:",
        "etiqueta_lugar": "Locación / Modalidad:",
        "etiqueta_detalle": "Paquete de Servicio / Entregables",
        "firma_izq": "Director Creativo / Productor",
        "firma_der": "Aprobación de Cotización y Términos",
        "color_primario": "#0EA5E9",
        "color_tabla": "#0C4A6E",
        "placeholder_prod": "Ej: Cobertura Fotográfica 4 hrs + Edición"
    },
    "Taller Mecánico / Soporte Técnico": {
        "titulo": "ORDEN DE SERVICIO Y DIAGNÓSTICO",
        "subtitulo": "Mantenimiento, Refacciones y Mano de Obra",
        "etiqueta_fecha": "FECHA PROMETIDA DE ENTREGA:",
        "etiqueta_lugar": "Datos de Unidad / Equipo:",
        "etiqueta_detalle": "Mano de Obra / Refacción / Diagnóstico",
        "firma_izq": "Técnico / Mecánico Responsable",
        "firma_der": "Autorización de Reparación y Retiro",
        "color_primario": "#F59E0B",
        "color_tabla": "#451A03",
        "placeholder_prod": "Ej: Cambio de balatas + Rectificado"
    },
    "Consultoría / Honorarios Profesionales": {
        "titulo": "COMPROBANTE DE HONORARIOS Y SERVICIOS",
        "subtitulo": "Asesoría Profesional y Consultoría",
        "etiqueta_fecha": "FECHA DE EMISIÓN / PERIODO:",
        "etiqueta_lugar": "Modalidad (Presencial / Remoto):",
        "etiqueta_detalle": "Concepto de Asesoría / Horas de Sesión",
        "firma_izq": "Consultor / Profesional",
        "firma_der": "Aceptación de Informe o Sesión",
        "color_primario": "#334155",
        "color_tabla": "#1E293B",
        "placeholder_prod": "Ej: Auditoría administrativa y financiera (10 hrs)"
    }
}

# =========================================================
# PANEL LATERAL: CONFIGURACIÓN UNIVERSAL DEL NEGOCIO
# =========================================================
with st.sidebar:
    st.header("⚡ Configuración del Negocio")
    
    giro_seleccionado = st.selectbox("Giro Comercial (Preset Rápido):", list(PRESETS_GIROS.keys()))
    preset = PRESETS_GIROS[giro_seleccionado]

    with st.expander("🏢 Identidad Comercial", expanded=True):
        negocio_nombre = st.text_input("Nombre de la Marca o Negocio", placeholder="Ej: Kairós MKT / Mi Taller")
        negocio_contacto = st.text_input("Teléfono, WhatsApp o Sitio Web", placeholder="Ej: WhatsApp: 981-123-4567")
        logo_file = st.file_uploader("Subir Logotipo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        logo_bytes = logo_file.getvalue() if logo_file else None

    with st.expander("📝 Vocabulario y Textos del Giro", expanded=False):
        titulo_doc = st.text_input("Título del Documento", value=preset["titulo"])
        subtitulo_doc = st.text_input("Subtítulo", value=preset["subtitulo"])
        lbl_fecha = st.text_input("Etiqueta de Fecha Operativa", value=preset["etiqueta_fecha"])
        lbl_lugar = st.text_input("Etiqueta de Ubicación/Lugar", value=preset["etiqueta_lugar"])
        lbl_detalle = st.text_input("Encabezado de Tabla (Conceptos)", value=preset["etiqueta_detalle"])
        mensaje_pie = st.text_area("Leyenda o Términos al Pie", value="Favor de verificar las condiciones y detalles descritos en este documento.")

    with st.expander("🎨 Colores y Estilo Visual", expanded=False):
        col_fondo = st.color_picker("Color de fondo de la hoja", "#FFFFFF")
        col_primario = st.color_picker("Color de acento principal", preset["color_primario"])
        col_tabla = st.color_picker("Color encabezado tabla", preset["color_tabla"])
        col_texto_tabla = st.color_picker("Color texto tabla", "#FFFFFF")

    with st.expander("💲 Moneda e Impuestos", expanded=False):
        simbolo_moneda = st.selectbox("Símbolo de Moneda", ["$", "USD $", "EUR €", "MXN $"], index=0)
        desglosar_iva = st.checkbox("Desglosar Impuesto (IVA/Tax)", value=False)
        tasa_iva = st.number_input("Tasa de Impuesto (%)", min_value=0.0, value=16.0, step=1.0)

    with st.expander("✍️ Bloque de Firmas y Validación", expanded=False):
        mostrar_firmas = st.checkbox("Incluir bloque de firmas", value=True)
        firma_izq = st.text_input("Firma izquierda", value=preset["firma_izq"])
        firma_der = st.text_input("Firma derecha", value=preset["firma_der"])

config_pdf_usuario = {
    "titulo_documento": titulo_doc,
    "subtitulo_documento": subtitulo_doc,
    "nombre_negocio": negocio_nombre,
    "contacto_negocio": negocio_contacto,
    "mensaje_pie": mensaje_pie,
    "etiqueta_fecha_operativa": lbl_fecha,
    "etiqueta_lugar_operativo": lbl_lugar,
    "etiqueta_detalle": lbl_detalle,
    "firma_izquierda": firma_izq,
    "firma_derecha": firma_der,
    "moneda": simbolo_moneda,
    "color_fondo_hoja": col_fondo,
    "color_primario": col_primario,
    "color_tabla_fondo": col_tabla,
    "color_tabla_texto": col_texto_tabla,
    "mostrar_firmas": mostrar_firmas,
    "desglosar_iva": desglosar_iva,
    "tasa_iva": tasa_iva,
    "logo_bytes": logo_bytes
}

# =========================================================
# CONTENIDO PRINCIPAL
# =========================================================
st.title("💼 Plataforma Comercial & Generador de Documentos")

pestana_registro, pestana_catalogo, pestana_historial = st.tabs([
    "📝 Registro & Previsualización", 
    "🏷️ Catálogo de Precios/Servicios", 
    "📊 Historial de Registros"
])

# --- PESTAÑA 1: REGISTRO Y PREVIEW DINÁMICO ---
with pestana_registro:
    col_izq, col_der = st.columns([1.1, 0.9])
    
    with col_izq:
        st.subheader("1. Datos Generales")
        f1, f2 = st.columns(2)
        with f1:
            folio_auto = f"DOC-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            folio = st.text_input("Folio / Código Único", value=folio_auto)
            cliente = st.text_input("Cliente / Empresa / Titular", placeholder="Ej: Constructora del Golfo S.A.")
            telefono = st.text_input("Teléfono / WhatsApp", placeholder="Ej: 981 123 4567")
            direccion = st.text_area(lbl_lugar.replace(":", ""), placeholder="Ej: Av. Principal #100 o Modalidad Online")

        with f2:
            fecha_entrega = st.date_input(lbl_fecha.replace(":", ""), min_value=datetime.date.today())
            tipo_horario = st.selectbox("Turno / Modalidad de Horario", ["Hora específica", "Rango predefinido", "Horario abierto / No aplica"])
            if tipo_horario == "Hora específica":
                hora_sel = st.time_input("Hora", value=datetime.time(12, 0))
                horario_entrega = hora_sel.strftime("%I:%M %p").lstrip("0")
            elif tipo_horario == "Rango predefinido":
                horario_entrega = st.selectbox("Rango", ["09:00 - 12:00", "12:00 - 15:00", "15:00 - 18:00", "18:00 - 21:00"])
            else:
                horario_entrega = "Horario abierto / Todo el día"

            anticipo = st.number_input(f"Anticipo / Adelanto ({simbolo_moneda})", min_value=0.0, step=50.0)
            estado_entrega = st.selectbox("Estado del Registro", ["Pendiente / Cotización", "En Proceso / Ruta", "Completado / Entregado", "Cancelado"])

        st.markdown("---")
        st.subheader("2. Conceptos, Productos o Servicios")
        cp1, cp2, cp3, cp4 = st.columns([3, 1, 1, 1])
        with cp1:
            prod_nom = st.text_input("Descripción del Concepto", placeholder=preset["placeholder_prod"])
        with cp2:
            prod_cant = st.number_input("Cant.", min_value=1, value=1, step=1)
        with cp3:
            prod_precio = st.number_input(f"P. Unitario ({simbolo_moneda})", min_value=0.0, step=10.0)
        with cp4:
            st.write("")
            st.write("")
            if st.button("➕ Agregar"):
                if prod_nom.strip():
                    st.session_state.partidas_actuales.append({
                        "producto": prod_nom.strip(),
                        "cantidad": int(prod_cant),
                        "precio_unitario": float(prod_precio),
                        "subtotal": float(prod_cant * prod_precio)
                    })
                    st.rerun()

        partidas_render = st.session_state.partidas_actuales if st.session_state.partidas_actuales else [
            {"producto": f"Ejemplo: {preset['placeholder_prod']}", "cantidad": 1, "precio_unitario": 500.0, "subtotal": 500.0}
        ]

        total_venta = sum(item["subtotal"] for item in partidas_render)
        saldo_pendiente = max(0.0, total_venta - anticipo)
        estado_pago = "Liquidado" if saldo_pendiente == 0.0 else ("Anticipo" if anticipo > 0 else "Pendiente")

        if st.session_state.partidas_actuales:
            st.table(st.session_state.partidas_actuales)
            btn_guardar, btn_limpiar = st.columns([2, 1])
            with btn_guardar:
                if st.button("💾 Guardar y Sincronizar Documento", type="primary", use_container_width=True):
                    if not cliente.strip():
                        st.error("Por favor, ingresa el nombre del cliente o empresa.")
                    else:
                        cabecera_data = {
                            "folio": folio,
                            "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "cliente": cliente,
                            "telefono": telefono if telefono.strip() else "S/N",
                            "direccion": direccion if direccion.strip() else "Local / No aplica",
                            "fecha_entrega": str(fecha_entrega),
                            "horario_entrega": horario_entrega,
                            "total": total_venta,
                            "anticipo": anticipo,
                            "saldo": saldo_pendiente,
                            "estado_pago": estado_pago,
                            "estado_entrega": estado_entrega
                        }
                        with st.spinner("Guardando en base de datos y Google Sheets..."):
                            db.guardar_registro_venta(cabecera_data, st.session_state.partidas_actuales, sincronizar_cloud=True)
                        st.session_state.ultima_venta = {
                            "cabecera": cabecera_data,
                            "partidas": list(st.session_state.partidas_actuales)
                        }
                        st.session_state.partidas_actuales = []
                        st.success(f"¡Registro {folio} guardado exitosamente!")
                        st.rerun()

            with btn_limpiar:
                if st.button("🗑️ Limpiar Conceptos", use_container_width=True):
                    st.session_state.partidas_actuales = []
                    st.rerun()

    # --- PANEL DERECHO: PREVISUALIZACIÓN EN VIVO ---
    with col_der:
        st.subheader("👁️ Vista Previa del Documento")
        
        cabecera_preview = {
            "folio": folio,
            "cliente": cliente if cliente.strip() else "Nombre del Cliente / Empresa",
            "telefono": telefono if telefono.strip() else "000 000 0000",
            "direccion": direccion if direccion.strip() else "Ubicación / Modalidad",
            "fecha_entrega": str(fecha_entrega),
            "horario_entrega": horario_entrega,
            "total": total_venta,
            "anticipo": anticipo,
            "saldo": saldo_pendiente
        }
        
        pdf_bytes_live = pdf_nota.generar_nota_pdf(
            cabecera_preview, 
            partidas_render, 
            config_personalizada=config_pdf_usuario
        )
        
        try:
            import pypdfium2 as pdfium
            pdf_doc = pdfium.PdfDocument(pdf_bytes_live)
            page = pdf_doc.get_page(0)
            bitmap = page.render(scale=2.0)
            pil_image = bitmap.to_pil()
            st.image(pil_image, caption=f"Diseño adaptado para: {giro_seleccionado}", use_container_width=True)
        except Exception:
            st.info("💡 Cambia los parámetros del menú lateral y descarga el PDF.")

        st.download_button(
            label=f"📄 Descargar PDF ({simbolo_moneda})",
            data=pdf_bytes_live,
            file_name=f"{titulo_doc.replace(' ', '_')}_{folio}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

# --- PESTAÑA 2: CATÁLOGO ---
with pestana_catalogo:
    st.subheader("Catálogo Maestro de Precios y Servicios")
    with st.form("form_catalogo"):
        nombre_prod = st.text_input("Nombre del Producto o Paquete de Servicio", placeholder="Ej: Sesión Fotográfica / Renta Silla")
        c1, c2, c3 = st.columns(3)
        with c1:
            costo = st.number_input("Costo Operativo Base ($)", min_value=0.0, step=10.0)
        with c2:
            margen = st.number_input("Margen de Ganancia (%)", min_value=0.0, value=35.0, step=5.0)
        with c3:
            precio_sugerido = costo * (1 + margen / 100)
            precio_final = st.number_input("Precio al Público ($)", value=float(precio_sugerido), step=10.0)
            
        guardar_prod = st.form_submit_button("Guardar en Catálogo")
        if guardar_prod:
            if nombre_prod.strip():
                with st.spinner("Guardando en catálogo..."):
                    db.guardar_producto(nombre_prod.strip(), costo, margen, precio_final, sincronizar_cloud=True)
                st.success(f"Concepto '{nombre_prod}' añadido al catálogo.")
            else:
                st.error("El nombre del concepto no puede estar vacío.")

# --- PESTAÑA 3: HISTORIAL ---
with pestana_historial:
    st.subheader("Historial de Transacciones Registradas")
    df_ventas = db.obtener_ventas()
    
    if df_ventas.empty:
        st.info("No hay registros en la base de datos.")
    else:
        st.dataframe(df_ventas, use_container_width=True)
        st.markdown("---")
        folio_elegido = st.selectbox("Selecciona un folio para regenerar su PDF con el diseño actual:", df_ventas["folio"].tolist())
        
        if folio_elegido:
            df_partidas = db.obtener_detalle_folio(folio_elegido)
            st.table(df_partidas)
            
            fila_cabecera = df_ventas[df_ventas["folio"] == folio_elegido].iloc[0].to_dict()
            partidas_list = df_partidas.to_dict(orient="records")
            
            pdf_reimpreso = pdf_nota.generar_nota_pdf(
                fila_cabecera, 
                partidas_list, 
                config_personalizada=config_pdf_usuario
            )
            
            st.download_button(
                label=f"📄 Descargar PDF de Folio {folio_elegido}",
                data=pdf_reimpreso,
                file_name=f"Documento_{folio_elegido}.pdf",
                mime="application/pdf"
            )

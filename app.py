import streamlit as st
import datetime
import uuid
import db
import pdf_nota

st.set_page_config(page_title="Sistema Comercial Multi-Giro & Comprobantes", layout="wide", page_icon="⚡")
db.init_db()

if "partidas_actuales" not in st.session_state:
    st.session_state.partidas_actuales = []
if "ultima_venta" not in st.session_state:
    st.session_state.ultima_venta = None

# =========================================================
# CATÁLOGO GENERAL DE PRESETS POR GIRO COMERCIAL
# =========================================================
CATALOGO_GIROS = {
    # Repostería, Panadería y Postres
    "Pastelería / Repostería / Panadería Artesanal": {
        "titulo": "NOTA DE PEDIDO Y REMISIÓN DE REPOSTERÍA",
        "subtitulo": "Pasteles de Diseño, Postres y Repostería Fina",
        "etiqueta_fecha": "FECHA DE ENTREGA DEL PEDIDO:",
        "etiqueta_lugar": "Lugar de Entrega / Mostrador:",
        "etiqueta_detalle": "Pastel / Postre / Porciones / Sabor y Temática",
        "firma_izq": "Elaborado por (Chef Pastelero/a)",
        "firma_der": "Recibido de Conformidad (Cliente)",
        "color_primario": "#DB2777",  # Rosa Pastel / Repostería
        "color_tabla": "#831843",
        "placeholder_prod": "Ej: Pastel 3 Leches 30 Personas relleno de Fresa con Temática"
    },

    # Aguas Naturales y Bebidas
    "Aguas Naturales / Paletería / Bebidas Artesanales": {
        "titulo": "NOTA DE VENTA Y DESPACHO DE BEBIDAS",
        "subtitulo": "Preparación de Aguas Naturales y Sabores Artesanales",
        "etiqueta_fecha": "FECHA DE SURTIDO / EVENTO:",
        "etiqueta_lugar": "Lugar de Entrega / Mostrador:",
        "etiqueta_detalle": "Sabor / Vitrolero / Litros / Presentación",
        "firma_izq": "Despachado por (Encargado/a)",
        "firma_der": "Recibido de Conformidad (Cliente)",
        "color_primario": "#059669",  # Verde Esmeralda Fresco
        "color_tabla": "#064E3B",
        "placeholder_prod": "Ej: Vitrolero 20L Horchata de Coco / Garrafa Jamaica"
    },

    # Prensa, Medios y Reportería
    "Prensa / Reportería / Cobertura Periodística": {
        "titulo": "ORDEN DE COBERTURA Y COMISIONES DE PRENSA",
        "subtitulo": "Servicios Periodísticos, Fotografía y Redacción Informativa",
        "etiqueta_fecha": "FECHA DE COBERTURA / EVENTO:",
        "etiqueta_lugar": "Sede / Locación de la Rueda de Prensa:",
        "etiqueta_detalle": "Servicio Periodístico / Nota / Entrevista / Reportaje",
        "firma_izq": "Reportero(a) / Periodista Asignado",
        "firma_der": "Aprobación de Cobertura y Medio",
        "color_primario": "#DC2626",  # Rojo Editorial Prensa
        "color_tabla": "#18181B",
        "placeholder_prod": "Ej: Cobertura Conferencia de Prensa + Nota Informativa + Galería"
    },

    # Marketing, Producción y Creativos
    "Agencia de Marketing / Producción Audiovisual": {
        "titulo": "COTIZACIÓN Y ORDEN DE SERVICIO CREATIVO",
        "subtitulo": "Marketing Digital, Campañas y Producción Audiovisual",
        "etiqueta_fecha": "FECHA DE ENTREGA / PRODUCCIÓN:",
        "etiqueta_lugar": "Modalidad (Online / Locación):",
        "etiqueta_detalle": "Entregable / Paquete de Campaña / Video",
        "firma_izq": "Director Creativo / Agencia",
        "firma_der": "Aceptación de Presupuesto (Cliente)",
        "color_primario": "#2563EB",
        "color_tabla": "#0F172A",
        "placeholder_prod": "Ej: Gestión de Redes Sociales mensual + 8 Reels"
    },

    # Mobiliario y Eventos
    "Renta de Mobiliario y Banquetes para Eventos": {
        "titulo": "CONTRATO Y REMISIÓN DE MOBILIARIO",
        "subtitulo": "Renta de Equipo, Mesas, Sillas y Toldos",
        "etiqueta_fecha": "FECHA DEL EVENTO / MONTAJE:",
        "etiqueta_lugar": "Dirección del Evento / Salón:",
        "etiqueta_detalle": "Mobiliario / Artículos en Renta",
        "firma_izq": "Entregado por (Chofer / Montador)",
        "firma_der": "Recibido en Buen Estado (Cliente)",
        "color_primario": "#7C3AED",
        "color_tabla": "#2E1065",
        "placeholder_prod": "Ej: 5 Mesas Tablón con Mantel + 50 Sillas Plegables"
    },

    # Talleres y Refacciones
    "Taller Mecánico / Refaccionaria / Llantera": {
        "titulo": "ORDEN DE SERVICIO Y DIAGNÓSTICO AUTOMOTRIZ",
        "subtitulo": "Mantenimiento Preventivo, Correctivo y Refacciones",
        "etiqueta_fecha": "FECHA ESTIMADA DE SALIDA:",
        "etiqueta_lugar": "Datos del Vehículo / Placas:",
        "etiqueta_detalle": "Refacción / Mano de Obra / Afinación",
        "firma_izq": "Mecánico Responsable",
        "firma_der": "Autorización de Trabajo y Retiro de Unidad",
        "color_primario": "#D97706",
        "color_tabla": "#451A03",
        "placeholder_prod": "Ej: Afinación Mayor + Cambio de Aceite Sintético 5W30"
    },

    # Alimentos y Restaurantes
    "Restaurante / Cafetería / Cocina Económica": {
        "titulo": "COMANDA Y CUENTA DE CONSUMO",
        "subtitulo": "Servicio de Alimentos, Bebidas y Banquetes",
        "etiqueta_fecha": "FECHA DE SERVICIO:",
        "etiqueta_lugar": "Mesa / Domicilio / Para Llevar:",
        "etiqueta_detalle": "Platillo / Bebida / Menú del Día",
        "firma_izq": "Atendido por (Capitán / Mesero)",
        "firma_der": "Firma del Comensal",
        "color_primario": "#EA580C",
        "color_tabla": "#431407",
        "placeholder_prod": "Ej: 3 Menús Ejecutivos del Día + Jarras de Agua"
    },

    # Artes Gráficas
    "Imprenta / Serigrafía / Rotulación": {
        "titulo": "ORDEN DE PRODUCCIÓN GRÁFICA Y REPARTO",
        "subtitulo": "Impresión Offset, Digital y Gran Formato",
        "etiqueta_fecha": "FECHA COMPROMISO DE ENTREGA:",
        "etiqueta_lugar": "Lugar de Entrega / Mostrador:",
        "etiqueta_detalle": "Especificación de Impresión / Millar / Acabado",
        "firma_izq": "Prensista / Taller Gráfico",
        "firma_der": "Visto Bueno y Recepción de Trabajo",
        "color_primario": "#0284C7",
        "color_tabla": "#082F49",
        "placeholder_prod": "Ej: 1,000 Volantes 1/4 carta couche 130g Full Color"
    },

    # Ferreterías y Materiales
    "Ferretería / Tlapalería / Materiales": {
        "titulo": "NOTA DE VENTA Y REMISIÓN DE MATERIALES",
        "subtitulo": "Ferretería, Pinturas, Plomería y Electricidad",
        "etiqueta_fecha": "FECHA DE ENVÍO / ENTREGA:",
        "etiqueta_lugar": "Dirección de Obra / Domicilio:",
        "etiqueta_detalle": "Material / Herramienta / Código",
        "firma_izq": "Despachado por (Bodega)",
        "firma_der": "Recibido de Conformidad en Obra",
        "color_primario": "#475569",
        "color_tabla": "#0F172A",
        "placeholder_prod": "Ej: 10 Bultos de Cemento Gris + 5 Varillas 3/8"
    },

    # Comercio General
    "Tienda de Abarrotes / Minisúper / Miscelánea": {
        "titulo": "TICKET Y NOTA DE COMPRA",
        "subtitulo": "Venta de Abarrotes y Productos de Consumo",
        "etiqueta_fecha": "FECHA DE COMPRA:",
        "etiqueta_lugar": "Caja / Reparto local:",
        "etiqueta_detalle": "Artículo / Marca / Gramaje",
        "firma_izq": "Atendió (Cajero)",
        "firma_der": "Cliente",
        "color_primario": "#16A34A",
        "color_tabla": "#14532D",
        "placeholder_prod": "Ej: Caja de Huevo 12kg + Aceite vegetal 1L"
    },

    # Escuelas y Cursos
    "Escuela / Kínder / Guardería / Academia": {
        "titulo": "RECIBO DE PAGO DE COLEGIATURA Y TALLERES",
        "subtitulo": "Servicios Educativos y Estancia Infantil",
        "etiqueta_fecha": "FECHA DE PAGO / MES:",
        "etiqueta_lugar": "Plantel / Grado y Grupo:",
        "etiqueta_detalle": "Concepto (Inscripción / Colegiatura / Materiales)",
        "firma_izq": "Administración Escolar",
        "firma_der": "Padre / Tutor",
        "color_primario": "#2563EB",
        "color_tabla": "#1E3A8A",
        "placeholder_prod": "Ej: Colegiatura del Mes de Agosto - Nivel Preescolar"
    },

    # Consultoría y Honorarios
    "Consultoría / Honorarios / Despacho": {
        "titulo": "RECIBO DE HONORARIOS Y ASESORÍA PROFESIONAL",
        "subtitulo": "Servicios Profesionales de Asesoría y Consultoría",
        "etiqueta_fecha": "FECHA DE EMISIÓN:",
        "etiqueta_lugar": "Modalidad (Oficina / Remoto):",
        "etiqueta_detalle": "Concepto de Honorarios / Horas de Consultoría",
        "firma_izq": "Consultor(a) Titular",
        "firma_der": "Aceptación de Servicios (Cliente)",
        "color_primario": "#334155",
        "color_tabla": "#0F172A",
        "placeholder_prod": "Ej: Auditoría y planeación administrativa (Paquete mensual)"
    }
}

# =========================================================
# PANEL LATERAL: CONFIGURACIÓN DINÁMICA
# =========================================================
with st.sidebar:
    st.header("⚡ Configuración del Negocio")
    
    lista_giros = list(CATALOGO_GIROS.keys())
    giro_seleccionado = st.selectbox(
        "🔍 Escribe o selecciona el Giro Comercial:",
        options=lista_giros,
        index=0,
        help="Escribe letras para buscar y filtrar automáticamente el giro comercial."
    )
    preset = CATALOGO_GIROS[giro_seleccionado]

    with st.expander("🏢 Datos de la Empresa / Marca", expanded=True):
        negocio_nombre = st.text_input("Nombre de la Marca", placeholder="Ej: Mi Empresa Comercial")
        negocio_contacto = st.text_input("Contacto / WhatsApp", placeholder="Ej: WhatsApp: 981 123 4567")
        logo_file = st.file_uploader("Subir Logotipo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        logo_bytes = logo_file.getvalue() if logo_file else None

    with st.expander("📝 Personalización de Textos", expanded=False):
        titulo_doc = st.text_input("Título del Documento", value=preset["titulo"])
        subtitulo_doc = st.text_input("Subtítulo", value=preset["subtitulo"])
        lbl_fecha = st.text_input("Etiqueta de Fecha", value=preset["etiqueta_fecha"])
        lbl_lugar = st.text_input("Etiqueta de Ubicación", value=preset["etiqueta_lugar"])
        lbl_detalle = st.text_input("Etiqueta de la Tabla", value=preset["etiqueta_detalle"])
        mensaje_pie = st.text_area("Leyenda al pie de página", value="Favor de revisar las especificaciones al momento de la entrega.")

    with st.expander("🎨 Colores de Marca", expanded=False):
        col_fondo = st.color_picker("Color de fondo de la hoja", "#FFFFFF")
        col_primario = st.color_picker("Color de acento principal", preset["color_primario"])
        col_tabla = st.color_picker("Color fondo encabezado tabla", preset["color_tabla"])
        col_texto_tabla = st.color_picker("Color texto encabezado tabla", "#FFFFFF")

    with st.expander("💲 Moneda e Impuestos (IVA)", expanded=True):
        simbolo_moneda = st.selectbox("Símbolo de Moneda", ["$", "MXN $", "USD $", "EUR €"], index=0)
        desglosar_iva = st.toggle("Activar Desglose de IVA / Impuesto", value=False)
        if desglosar_iva:
            tasa_iva = st.number_input("Tasa de IVA (%)", min_value=0.0, max_value=100.0, value=16.0, step=1.0)
        else:
            tasa_iva = 0.0

    with st.expander("✍️ Firmas de Conformidad", expanded=False):
        mostrar_firmas = st.checkbox("Incluir bloque de firmas", value=True)
        firma_izq = st.text_input("Texto firma izquierda", value=preset["firma_izq"])
        firma_der = st.text_input("Texto firma derecha", value=preset["firma_der"])

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

# --- PESTAÑA 1: REGISTRO Y PREVIEW ---
with pestana_registro:
    col_izq, col_der = st.columns([1.1, 0.9])
    
    with col_izq:
        st.subheader("1. Datos Generales")
        f1, f2 = st.columns(2)
        with f1:
            folio_auto = f"DOC-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            folio = st.text_input("Folio / ID", value=folio_auto)
            cliente = st.text_input("Cliente / Empresa / Titular", placeholder="Ej: Eventos del Sureste / Juan Gómez")
            telefono = st.text_input("Teléfono / WhatsApp", placeholder="Ej: 981 123 4567")
            direccion = st.text_area(lbl_lugar.replace(":", ""), placeholder="Ej: Calle Principal #100 o Mostrador")

        with f2:
            fecha_entrega = st.date_input(lbl_fecha.replace(":", ""), min_value=datetime.date.today())
            tipo_horario = st.selectbox("Modalidad de Horario", ["Hora específica", "Rango predefinido", "Horario abierto / No aplica"])
            if tipo_horario == "Hora específica":
                hora_sel = st.time_input("Hora", value=datetime.time(12, 0))
                horario_entrega = hora_sel.strftime("%I:%M %p").lstrip("0")
            elif tipo_horario == "Rango predefinido":
                horario_entrega = st.selectbox("Rango", ["09:00 - 12:00", "12:00 - 15:00", "15:00 - 18:00", "18:00 - 21:00"])
            else:
                horario_entrega = "Horario abierto / Todo el día"

            anticipo = st.number_input(f"Anticipo Pagado ({simbolo_moneda})", min_value=0.0, step=50.0)
            estado_entrega = st.selectbox("Estado del Registro", ["Pendiente / Por Entregar", "En Proceso / Ruta", "Completado / Entregado", "Cancelado"])

        st.markdown("---")
        st.subheader("2. Conceptos, Productos o Servicios")
        cp1, cp2, cp3, cp4 = st.columns([3, 1, 1, 1])
        with cp1:
            prod_nom = st.text_input("Descripción", placeholder=preset["placeholder_prod"])
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
            {"producto": f"Muestra: {preset['placeholder_prod']}", "cantidad": 1, "precio_unitario": 0.0, "subtotal": 0.0}
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
                        st.error("Por favor, ingresa el nombre del cliente.")
                    else:
                        cabecera_data = {
                            "folio": folio,
                            "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "cliente": cliente,
                            "telefono": telefono if telefono.strip() else "S/N",
                            "direccion": direccion if direccion.strip() else "Mostrador",
                            "fecha_entrega": str(fecha_entrega),
                            "horario_entrega": horario_entrega,
                            "total": total_venta,
                            "anticipo": anticipo,
                            "saldo": saldo_pendiente,
                            "estado_pago": estado_pago,
                            "estado_entrega": estado_entrega
                        }
                        with st.spinner("Guardando localmente y en Google Sheets..."):
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
            "cliente": cliente if cliente.strip() else "Nombre del Cliente",
            "telefono": telefono if telefono.strip() else "000 000 0000",
            "direccion": direccion if direccion.strip() else "Ubicación / Mostrador",
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
            st.image(pil_image, caption=f"Giro actual: {giro_seleccionado}", use_container_width=True)
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
    st.subheader("Catálogo de Precios y Servicios")
    with st.form("form_catalogo"):
        nombre_prod = st.text_input("Nombre del Producto o Servicio", placeholder="Ej: Garrafa Horchata 20L / Pastel 3 Leches / Cobertura Prensa")
        c1, c2, c3 = st.columns(3)
        with c1:
            costo = st.number_input("Costo Base ($)", min_value=0.0, step=10.0)
        with c2:
            margen = st.number_input("Margen Deseado (%)", min_value=0.0, value=35.0, step=5.0)
        with c3:
            precio_sugerido = costo * (1 + margen / 100)
            precio_final = st.number_input("Precio al Público ($)", value=float(precio_sugerido), step=10.0)
            
        guardar_prod = st.form_submit_button("Guardar en Catálogo")
        if guardar_prod:
            if nombre_prod.strip():
                with st.spinner("Guardando en catálogo..."):
                    db.guardar_producto(nombre_prod.strip(), costo, margen, precio_final, sincronizar_cloud=True)
                st.success(f"'{nombre_prod}' registrado en catálogo.")
            else:
                st.error("El nombre no puede estar vacío.")

# --- PESTAÑA 3: HISTORIAL ---
with pestana_historial:
    st.subheader("Historial de Registros")
    df_ventas = db.obtener_ventas()
    
    if df_ventas.empty:
        st.info("No hay registros en la base de datos.")
    else:
        st.dataframe(df_ventas, use_container_width=True)
        st.markdown("---")
        folio_elegido = st.selectbox("Selecciona un folio para regenerar su PDF:", df_ventas["folio"].tolist())
        
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

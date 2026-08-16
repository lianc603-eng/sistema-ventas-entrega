import streamlit as st
import datetime
import uuid
import db
import pdf_nota

st.set_page_config(page_title="Sistema de Ventas y Entregas", layout="wide", page_icon="📦")
db.init_db()

if "partidas_actuales" not in st.session_state:
    st.session_state.partidas_actuales = []
if "ultima_venta" not in st.session_state:
    st.session_state.ultima_venta = None

# =========================================================
# PANEL LATERAL: PERSONALIZACIÓN EN VIVO
# =========================================================
with st.sidebar:
    st.header("🎨 Diseño del Comprobante")
    
    with st.expander("🏢 Identidad de Marca", expanded=True):
        negocio_nombre = st.text_input("Nombre de Empresa", value="Mi Negocio Comercial")
        negocio_contacto = st.text_input("Contacto", value="WhatsApp: 55-1234-5678")
        logo_file = st.file_uploader("Subir Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        logo_bytes = logo_file.getvalue() if logo_file else None

    with st.expander("📄 Textos y Títulos", expanded=False):
        titulo_doc = st.text_input("Título", value="NOTA DE VENTA Y REMISIÓN")
        subtitulo_doc = st.text_input("Subtítulo", value="Comprobante de Entrega y Despacho")
        mensaje_pie = st.text_area("Pie de página", value="Favor de revisar el producto al momento de su entrega.")

    with st.expander("🎨 Paleta de Colores", expanded=True):
        col_fondo = st.color_picker("Color de fondo de la hoja", "#FFFFFF")
        col_primario = st.color_picker("Color de acento (Franja/Destacados)", "#10B981")
        col_tabla = st.color_picker("Color fondo encabezado tabla", "#1E293B")
        col_texto_tabla = st.color_picker("Color texto encabezado tabla", "#FFFFFF")

    with st.expander("✍️ Firmas de Conformidad", expanded=False):
        mostrar_firmas = st.checkbox("Mostrar firmas", value=True)
        firma_izq = st.text_input("Firma izquierda", value="Entregado por (Vendedor/Repartidor)")
        firma_der = st.text_input("Firma derecha", value="Firma de Recibido de Conformidad (Cliente)")

# Configuración unificada para pasar a pdf_nota
config_pdf_usuario = {
    "titulo_documento": titulo_doc,
    "subtitulo_documento": subtitulo_doc,
    "nombre_negocio": negocio_nombre,
    "contacto_negocio": negocio_contacto,
    "mensaje_pie": mensaje_pie,
    "firma_izquierda": firma_izq,
    "firma_derecha": firma_der,
    "color_fondo_hoja": col_fondo,
    "color_primario": col_primario,
    "color_tabla_fondo": col_tabla,
    "color_tabla_texto": col_texto_tabla,
    "mostrar_firmas": mostrar_firmas,
    "logo_bytes": logo_bytes
}

# =========================================================
# CONTENIDO PRINCIPAL
# =========================================================
st.title("📦 Sistema de Gestión de Ventas y Entregas")

pestana_venta, pestana_catalogo, pestana_historial = st.tabs([
    "📝 Nueva Venta & Preview", 
    "🏷️ Catálogo de Productos", 
    "📊 Historial de Ventas"
])

# --- PESTAÑA 1: NUEVA VENTA CON PREVIEW EN VIVO ---
with pestana_venta:
    col_izq, col_der = st.columns([1.1, 0.9])
    
    with col_izq:
        st.subheader("1. Datos de Venta y Entrega")
        f1, f2 = st.columns(2)
        with f1:
            folio_auto = f"V-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            folio = st.text_input("Folio", value=folio_auto)
            cliente = st.text_input("Nombre del Cliente", value="Consumidor Final")
            telefono = st.text_input("Teléfono", value="5500000000")
            direccion = st.text_area("Lugar de Entrega", value="Mostrador")

        with f2:
            fecha_entrega = st.date_input("Fecha de Entrega", min_value=datetime.date.today())
            tipo_horario = st.selectbox("Modalidad de Horario", ["Hora específica", "Rango predefinido", "Horario abierto"])
            if tipo_horario == "Hora específica":
                hora_sel = st.time_input("Hora", value=datetime.time(12, 0))
                horario_entrega = hora_sel.strftime("%I:%M %p").lstrip("0")
            elif tipo_horario == "Rango predefinido":
                horario_entrega = st.selectbox("Rango", ["09:00 - 12:00", "12:00 - 15:00", "15:00 - 18:00", "18:00 - 21:00"])
            else:
                horario_entrega = "Horario abierto"

            anticipo = st.number_input("Anticipo Pagado ($)", min_value=0.0, step=50.0)
            estado_entrega = st.selectbox("Estado", ["Pendiente", "En Ruta", "Entregado", "Cancelado"])

        st.markdown("---")
        st.subheader("2. Partidas / Artículos")
        cp1, cp2, cp3, cp4 = st.columns([3, 1, 1, 1])
        with cp1:
            prod_nom = st.text_input("Descripción")
        with cp2:
            prod_cant = st.number_input("Cant.", min_value=1, value=1, step=1)
        with cp3:
            prod_precio = st.number_input("P. Unitario ($)", min_value=0.0, step=10.0)
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
            {"producto": "Producto de Ejemplo", "cantidad": 1, "precio_unitario": 250.0, "subtotal": 250.0}
        ]

        total_venta = sum(item["subtotal"] for item in partidas_render)
        saldo_pendiente = max(0.0, total_venta - anticipo)
        estado_pago = "Liquidado" if saldo_pendiente == 0.0 else ("Anticipo" if anticipo > 0 else "Pendiente")

        if st.session_state.partidas_actuales:
            st.table(st.session_state.partidas_actuales)
            btn_guardar, btn_limpiar = st.columns([2, 1])
            with btn_guardar:
                if st.button("💾 Guardar y Sincronizar Venta", type="primary", use_container_width=True):
                    cabecera_data = {
                        "folio": folio,
                        "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": cliente,
                        "telefono": telefono,
                        "direccion": direccion,
                        "fecha_entrega": str(fecha_entrega),
                        "horario_entrega": horario_entrega,
                        "total": total_venta,
                        "anticipo": anticipo,
                        "saldo": saldo_pendiente,
                        "estado_pago": estado_pago,
                        "estado_entrega": estado_entrega
                    }
                    with st.spinner("Guardando en base local y Google Sheets..."):
                        db.guardar_registro_venta(cabecera_data, st.session_state.partidas_actuales, sincronizar_cloud=True)
                    st.session_state.ultima_venta = {
                        "cabecera": cabecera_data,
                        "partidas": list(st.session_state.partidas_actuales)
                    }
                    st.session_state.partidas_actuales = []
                    st.success(f"¡Venta {folio} guardada exitosamente!")
                    st.rerun()

            with btn_limpiar:
                if st.button("🗑️ Limpiar Partidas", use_container_width=True):
                    st.session_state.partidas_actuales = []
                    st.rerun()

    # --- PANEL DERECHO: PREVISUALIZACIÓN DEL PDF EN TIEMPO REAL ---
    with col_der:
        st.subheader("👁️ Vista Previa del PDF")
        
        cabecera_preview = {
            "folio": folio,
            "cliente": cliente if cliente.strip() else "Consumidor Final",
            "telefono": telefono,
            "direccion": direccion,
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
        
        # Renderizado de la página en imagen para evitar bloqueos del navegador
        try:
            import pypdfium2 as pdfium
            pdf_doc = pdfium.PdfDocument(pdf_bytes_live)
            page = pdf_doc.get_page(0)
            bitmap = page.render(scale=2.0)
            pil_image = bitmap.to_pil()
            st.image(pil_image, caption="Previsualización en tiempo real", use_container_width=True)
        except Exception:
            st.info("💡 Cambia los colores o datos y descarga el PDF con el botón de abajo.")

        st.download_button(
            label="📄 Descargar PDF Actual",
            data=pdf_bytes_live,
            file_name=f"Nota_Venta_{folio}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

# --- PESTAÑA 2: CATÁLOGO ---
with pestana_catalogo:
    st.subheader("Alta de Producto al Catálogo")
    with st.form("form_catalogo"):
        nombre_prod = st.text_input("Nombre / Descripción del Producto")
        c1, c2, c3 = st.columns(3)
        with c1:
            costo = st.number_input("Costo Base ($)", min_value=0.0, step=10.0)
        with c2:
            margen = st.number_input("Margen Deseado (%)", min_value=0.0, value=30.0, step=5.0)
        with c3:
            precio_sugerido = costo * (1 + margen / 100)
            precio_final = st.number_input("Precio de Venta ($)", value=float(precio_sugerido), step=10.0)
            
        guardar_prod = st.form_submit_button("Guardar en Catálogo")
        if guardar_prod:
            if nombre_prod.strip():
                with st.spinner("Guardando..."):
                    db.guardar_producto(nombre_prod.strip(), costo, margen, precio_final, sincronizar_cloud=True)
                st.success(f"Producto '{nombre_prod}' registrado con éxito.")
            else:
                st.error("El nombre del producto no puede quedar vacío.")

# --- PESTAÑA 3: HISTORIAL ---
with pestana_historial:
    st.subheader("Historial de Ventas")
    df_ventas = db.obtener_ventas()
    
    if df_ventas.empty:
        st.info("No hay ventas registradas en la base local.")
    else:
        st.dataframe(df_ventas, use_container_width=True)
        st.markdown("---")
        folio_elegido = st.selectbox("Selecciona un folio para reimprimir:", df_ventas["folio"].tolist())
        
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
                file_name=f"Nota_Venta_{folio_elegido}.pdf",
                mime="application/pdf"
            )

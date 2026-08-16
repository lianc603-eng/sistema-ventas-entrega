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
# PANEL LATERAL: PERSONALIZACIÓN DEL PDF EN TIEMPO REAL
# =========================================================
with st.sidebar:
    st.header("🎨 Personalización del PDF")
    
    with st.expander("🏢 Identidad del Negocio", expanded=True):
        negocio_nombre = st.text_input("Nombre comercial", value="Mi Empresa / Agencia")
        negocio_contacto = st.text_input("Teléfono / Contacto", value="WhatsApp: 55-0000-0000")
        logo_file = st.file_uploader("Logo (PNG o JPG)", type=["png", "jpg", "jpeg"])
        logo_bytes = logo_file.getvalue() if logo_file else None

    with st.expander("📄 Textos y Títulos", expanded=False):
        titulo_doc = st.text_input("Título Principal", value="NOTA DE VENTA Y REMISIÓN")
        subtitulo_doc = st.text_input("Subtítulo", value="Comprobante de Entrega y Despacho")
        mensaje_pie = st.text_area("Leyenda al pie de página", value="Favor de revisar el producto al momento de su entrega.")

    with st.expander("🎨 Colores de Marca", expanded=False):
        col_primario = st.color_picker("Color de acento (Franja/Destacados)", "#10B981")
        col_tabla = st.color_picker("Color encabezado de tabla", "#1E293B")
        col_texto_tabla = st.color_picker("Color texto encabezado tabla", "#FFFFFF")

    with st.expander("✍️ Firmas de Conformidad", expanded=False):
        mostrar_firmas = st.checkbox("Incluir bloque de firmas", value=True)
        firma_izq = st.text_input("Texto firma izquierda", value="Entregado por (Vendedor/Repartidor)")
        firma_der = st.text_input("Texto firma derecha", value="Firma de Recibido de Conformidad (Cliente)")

# Diccionario unificado de configuración
config_pdf_usuario = {
    "titulo_documento": titulo_doc,
    "subtitulo_documento": subtitulo_doc,
    "nombre_negocio": negocio_nombre,
    "contacto_negocio": negocio_contacto,
    "mensaje_pie": mensaje_pie,
    "firma_izquierda": firma_izq,
    "firma_derecha": firma_der,
    "color_primario": col_primario,
    "color_tabla_fondo": col_tabla,
    "color_tabla_texto": col_texto_tabla,
    "mostrar_firmas": mostrar_firmas,
    "logo_bytes": logo_bytes
}

# =========================================================
# CONTENIDO PRINCIPAL DE LA APLICACIÓN
# =========================================================
st.title("📦 Sistema de Gestión de Ventas y Entregas")

pestana_venta, pestana_catalogo, pestana_historial = st.tabs([
    "📝 Nueva Venta", 
    "🏷️ Catálogo de Productos", 
    "📊 Historial de Ventas"
])

# --- PESTAÑA 1: NUEVA VENTA ---
with pestana_venta:
    st.subheader("Datos de la Venta y Entrega")
    col1, col2 = st.columns(2)
    
    with col1:
        folio_auto = f"V-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        folio = st.text_input("Folio", value=folio_auto)
        cliente = st.text_input("Nombre del Cliente")
        telefono = st.text_input("Teléfono")
        direccion = st.text_area("Dirección / Lugar de Entrega", value="Mostrador")

    with col2:
        fecha_entrega = st.date_input("Fecha de Entrega", min_value=datetime.date.today())
        
        tipo_horario = st.selectbox("Modalidad de Horario", [
            "Hora específica", 
            "Rango predefinido", 
            "Horario abierto"
        ])
        
        if tipo_horario == "Hora específica":
            hora_sel = st.time_input("Selecciona la hora de entrega", value=datetime.time(12, 0))
            horario_entrega = hora_sel.strftime("%I:%M %p").lstrip("0")
        elif tipo_horario == "Rango predefinido":
            horario_entrega = st.selectbox("Rango acordado", [
                "09:00 - 12:00", 
                "12:00 - 15:00", 
                "15:00 - 18:00", 
                "18:00 - 21:00"
            ])
        else:
            horario_entrega = "Horario abierto"

        anticipo = st.number_input("Anticipo Pagado ($)", min_value=0.0, step=50.0)
        estado_entrega = st.selectbox("Estado de Entrega", ["Pendiente", "En Ruta", "Entregado", "Cancelado"])

    st.markdown("---")
    st.subheader("Desglose de Productos / Artículos")
    
    col_p1, col_p2, col_p3, col_p4 = st.columns([3, 1, 1, 1])
    with col_p1:
        prod_nom = st.text_input("Descripción del Producto")
    with col_p2:
        prod_cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
    with col_p3:
        prod_precio = st.number_input("Precio Unitario ($)", min_value=0.0, step=10.0)
    with col_p4:
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
            else:
                st.warning("Ingresa el nombre o descripción del producto.")

    if st.session_state.partidas_actuales:
        st.table(st.session_state.partidas_actuales)
        
        total_venta = sum(item["subtotal"] for item in st.session_state.partidas_actuales)
        saldo_pendiente = max(0.0, total_venta - anticipo)
        estado_pago = "Liquidado" if saldo_pendiente == 0.0 else ("Anticipo" if anticipo > 0 else "Pendiente")

        m1, m2 = st.columns(2)
        m1.metric("Total de la Venta", f"${total_venta:,.2f}")
        m2.metric("Saldo a Cobrar", f"${saldo_pendiente:,.2f}")

        btn_guardar, btn_limpiar = st.columns([2, 1])
        with btn_guardar:
            if st.button("💾 Guardar Venta y Sincronizar", type="primary", use_container_width=True):
                if not cliente.strip():
                    st.error("Por favor, ingresa el nombre del cliente.")
                else:
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
                    
                    with st.spinner("Guardando localmente y sincronizando a Google Sheets..."):
                        db.guardar_registro_venta(cabecera_data, st.session_state.partidas_actuales, sincronizar_cloud=True)
                    
                    st.session_state.ultima_venta = {
                        "cabecera": cabecera_data,
                        "partidas": list(st.session_state.partidas_actuales)
                    }
                    st.session_state.partidas_actuales = []
                    st.success(f"¡Venta {folio} registrada correctamente!")
                    st.rerun()

        with btn_limpiar:
            if st.button("🗑️ Limpiar Partidas", use_container_width=True):
                st.session_state.partidas_actuales = []
                st.rerun()

    # Descarga directa del PDF personalizado
    if st.session_state.ultima_venta:
        st.markdown("---")
        folio_reciente = st.session_state.ultima_venta["cabecera"]["folio"]
        st.success(f"Comprobante listo para el folio: **{folio_reciente}**")
        
        pdf_bytes = pdf_nota.generar_nota_pdf(
            st.session_state.ultima_venta["cabecera"], 
            st.session_state.ultima_venta["partidas"],
            config_personalizada=config_pdf_usuario
        )
        
        st.download_button(
            label=f"📄 Descargar Comprobante PDF Personalizado ({folio_reciente})",
            data=pdf_bytes,
            file_name=f"Nota_Venta_{folio_reciente}.pdf",
            mime="application/pdf",
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
                with st.spinner("Guardando producto..."):
                    db.guardar_producto(nombre_prod.strip(), costo, margen, precio_final, sincronizar_cloud=True)
                st.success(f"Producto '{nombre_prod}' registrado.")
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
        st.subheader("Reimprimir o Consultar Detalle")
        folios_disponibles = df_ventas["folio"].tolist()
        folio_elegido = st.selectbox("Selecciona un folio:", folios_disponibles)
        
        if folio_elegido:
            df_partidas = db.obtener_detalle_folio(folio_elegido)
            st.write(f"**Partidas del folio:** `{folio_elegido}`")
            st.table(df_partidas)
            
            fila_cabecera = df_ventas[df_ventas["folio"] == folio_elegido].iloc[0].to_dict()
            partidas_list = df_partidas.to_dict(orient="records")
            
            pdf_reimpreso = pdf_nota.generar_nota_pdf(
                fila_cabecera, 
                partidas_list, 
                config_personalizada=config_pdf_usuario
            )
            
            st.download_button(
                label=f"📄 Descargar PDF Personalizado de Folio {folio_elegido}",
                data=pdf_reimpreso,
                file_name=f"Nota_Venta_{folio_elegido}.pdf",
                mime="application/pdf"
            )

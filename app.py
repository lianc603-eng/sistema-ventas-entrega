import streamlit as st
import datetime
import uuid
import db
import pdf_nota

st.set_page_config(page_title="Sistema de Ventas y Entregas", layout="wide", page_icon="📦")

# 1. Inicializar base de datos local SQLite
db.init_db()

# 2. Inicializar variables de estado en la sesión
if "partidas_actuales" not in st.session_state:
    st.session_state.partidas_actuales = []
if "ultima_venta" not in st.session_state:
    st.session_state.ultima_venta = None

st.title("📦 Sistema de Gestión de Ventas y Entregas")

pestana_venta, pestana_catalogo, pestana_historial = st.tabs([
    "📝 Nueva Venta", 
    "🏷️ Catálogo de Productos", 
    "📊 Historial de Ventas"
])

# =========================================================
# PESTAÑA 1: REGISTRO DE NUEVA VENTA Y GENERACIÓN DE NOTA
# =========================================================
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
        horario_entrega = st.selectbox("Horario Acordado", [
            "Horario abierto",
            "09:00 - 12:00", 
            "12:00 - 15:00", 
            "15:00 - 18:00", 
            "18:00 - 21:00"
        ])
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
                st.warning("Ingresa la descripción del producto.")

    # Mostrar tabla y calcular balances si hay partidas agregadas
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

    # Descarga directa del PDF de la última venta registrada
    if st.session_state.ultima_venta:
        st.markdown("---")
        folio_reciente = st.session_state.ultima_venta["cabecera"]["folio"]
        st.success(f"Nota lista para el folio: **{folio_reciente}**")
        
        pdf_bytes = pdf_nota.generar_nota_pdf(
            st.session_state.ultima_venta["cabecera"], 
            st.session_state.ultima_venta["partidas"]
        )
        
        st.download_button(
            label=f"📄 Descargar Comprobante PDF ({folio_reciente})",
            data=pdf_bytes,
            file_name=f"Nota_Venta_{folio_reciente}.pdf",
            mime="application/pdf",
            type="secondary"
        )

# =========================================================
# PESTAÑA 2: CATÁLOGO DE PRODUCTOS
# =========================================================
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
                st.success(f"Producto '{nombre_prod}' registrado en base y Google Sheets.")
            else:
                st.error("El nombre del producto no puede quedar vacío.")

# =========================================================
# PESTAÑA 3: HISTORIAL DE VENTAS Y REIMPRESIÓN DE PDF
# =========================================================
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
        folio_elegido = st.selectbox("Selecciona un folio para ver partidas o generar PDF:", folios_disponibles)
        
        if folio_elegido:
            df_partidas = db.obtener_detalle_folio(folio_elegido)
            st.write(f"**Partidas del folio:** `{folio_elegido}`")
            st.table(df_partidas)
            
            # Recuperar datos de cabecera seleccionada para reconstruir el PDF
            fila_cabecera = df_ventas[df_ventas["folio"] == folio_elegido].iloc[0].to_dict()
            partidas_list = df_partidas.to_dict(orient="records")
            
            pdf_reimpreso = pdf_nota.generar_nota_pdf(fila_cabecera, partidas_list)
            
            st.download_button(
                label=f"📄 Descargar PDF de Folio {folio_elegido}",
                data=pdf_reimpreso,
                file_name=f"Nota_Venta_{folio_elegido}.pdf",
                mime="application/pdf"
            )

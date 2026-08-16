import streamlit as st
import datetime
import uuid
import db

st.set_page_config(page_title="Gestión de Ventas y Catálogo", layout="wide", page_icon="📦")

# Inicializar tablas al arrancar la app
db.init_db()

# Inicializar lista temporal de partidas en la sesión
if "partidas_actuales" not in st.session_state:
    st.session_state.partidas_actuales = []

st.title("📦 Sistema de Ventas y Entregas")

pestana_venta, pestana_producto, pestana_historial = st.tabs([
    "📝 Nueva Venta", 
    "🏷️ Catálogo de Productos", 
    "📊 Historial de Ventas"
])

# ==========================================
# 1. PESTAÑA: NUEVA VENTA
# ==========================================
with pestana_venta:
    st.subheader("Datos de la Venta y Entrega")
    col1, col2 = st.columns(2)
    
    with col1:
        folio_auto = f"V-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        folio = st.text_input("Folio", value=folio_auto)
        cliente = st.text_input("Nombre del Cliente")
        telefono = st.text_input("Teléfono")
        direccion = st.text_area("Dirección de Entrega")

    with col2:
        fecha_entrega = st.date_input("Fecha de Entrega", min_value=datetime.date.today())
        horario_entrega = st.selectbox("Horario de Entrega", [
            "09:00 - 12:00", 
            "12:00 - 15:00", 
            "15:00 - 18:00", 
            "18:00 - 21:00",
            "Horario Abierto"
        ])
        anticipo = st.number_input("Anticipo pagado ($)", min_value=0.0, step=50.0)
        estado_entrega = st.selectbox("Estado de Entrega", ["Pendiente", "En Ruta", "Entregado", "Cancelado"])

    st.markdown("---")
    st.subheader("Partidas / Productos de la Venta")
    
    # Formulario para agregar productos a la venta actual
    col_prod, col_cant, col_precio, col_btn = st.columns([3, 1, 1, 1])
    with col_prod:
        prod_nombre = st.text_input("Producto")
    with col_cant:
        prod_cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
    with col_precio:
        prod_precio = st.number_input("Precio Unitario ($)", min_value=0.0, step=10.0)
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Agregar"):
            if prod_nombre.strip():
                st.session_state.partidas_actuales.append({
                    "producto": prod_nombre.strip(),
                    "cantidad": int(prod_cant),
                    "precio_unitario": float(prod_precio),
                    "subtotal": float(prod_cant * prod_precio)
                })
                st.rerun()
            else:
                st.warning("Escribe el nombre del producto.")

    # Mostrar tabla con partidas acumuladas
    if st.session_state.partidas_actuales:
        st.table(st.session_state.partidas_actuales)
        total_calculado = sum(item["subtotal"] for item in st.session_state.partidas_actuales)
        saldo_calculado = max(0.0, total_calculado - anticipo)
        
        estado_pago = "Liquidado" if saldo_calculado == 0.0 else ("Anticipo" if anticipo > 0 else "Pendiente")

        st.metric(label="Total de la Venta", value=f"${total_calculado:,.2f}")
        st.metric(label="Saldo Pendiente", value=f"${saldo_calculado:,.2f}")

        col_guardar, col_limpiar = st.columns([2, 1])
        with col_guardar:
            if st.button("💾 Guardar Venta y Sincronizar", type="primary", use_container_width=True):
                if not cliente.strip():
                    st.error("Debes ingresar el nombre del cliente.")
                else:
                    cabecera = {
                        "folio": folio,
                        "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": cliente,
                        "telefono": telefono,
                        "direccion": direccion,
                        "fecha_entrega": str(fecha_entrega),
                        "horario_entrega": horario_entrega,
                        "total": total_calculado,
                        "anticipo": anticipo,
                        "saldo": saldo_calculado,
                        "estado_pago": estado_pago,
                        "estado_entrega": estado_entrega
                    }
                    
                    with st.spinner("Guardando en base local y sincronizando a Google Sheets..."):
                        db.guardar_registro_venta(cabecera, st.session_state.partidas_actuales, sincronizar_cloud=True)
                    
                    st.success(f"¡Venta con folio {folio} guardada exitosamente!")
                    st.session_state.partidas_actuales = []
                    st.rerun()

        with col_limpiar:
            if st.button("🗑️ Limpiar Partidas", use_container_width=True):
                st.session_state.partidas_actuales = []
                st.rerun()

# ==========================================
# 2. PESTAÑA: CATÁLOGO DE PRODUCTOS
# ==========================================
with pestana_producto:
    st.subheader("Registrar Nuevo Producto al Catálogo")
    with st.form("form_producto"):
        p_nombre = st.text_input("Nombre del Producto")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_costo = st.number_input("Costo Base ($)", min_value=0.0, step=10.0)
        with c2:
            p_margen = st.number_input("Margen (%)", min_value=0.0, value=30.0, step=5.0)
        with c3:
            precio_sugerido = p_costo * (1 + p_margen / 100)
            p_venta = st.number_input("Precio de Venta Final ($)", value=float(precio_sugerido), step=10.0)
        
        btn_prod = st.form_submit_button("Guardar en Catálogo")
        if btn_prod:
            if p_nombre.strip():
                with st.spinner("Guardando producto..."):
                    db.guardar_producto(p_nombre.strip(), p_costo, p_margen, p_venta, sincronizar_cloud=True)
                st.success(f"Producto '{p_nombre}' guardado y sincronizado a Google Sheets.")
            else:
                st.error("El nombre del producto no puede estar vacío.")

# ==========================================
# 3. PESTAÑA: HISTORIAL DE VENTAS
# ==========================================
with pestana_historial:
    st.subheader("Ventas Registradas (SQLite Local)")
    df_ventas = db.obtener_ventas()
    
    if df_ventas.empty:
        st.info("No hay ventas registradas aún.")
    else:
        st.dataframe(df_ventas, use_container_width=True)
        
        folio_sel = st.selectbox("Selecciona un Folio para ver su detalle:", df_ventas["folio"].tolist())
        if folio_sel:
            st.write(f"**Partidas del folio:** `{folio_sel}`")
            df_detalle = db.obtener_detalle_folio(folio_sel)
            st.table(df_detalle)

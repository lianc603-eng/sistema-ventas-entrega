import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
from db import init_db, guardar_registro_venta, obtener_ventas, obtener_detalle_folio
from pdf_nota import generar_nota_pdf

st.set_page_config(page_title="Punto de Venta y Entregas", page_icon="📦", layout="wide")

init_db()

st.title("📦 Sistema de Registro de Ventas y Despacho")

tab_nueva_venta, tab_consultas = st.tabs(["📝 Registrar Venta", "📋 Historial y Entregas"])

# ==================== PESTAÑA 1: NUEVA VENTA ====================
with tab_nueva_venta:
    if "articulos_venta" not in st.session_state:
        st.session_state.articulos_venta = []

    c_izq, c_der = st.columns([1, 1], gap="large")

    with c_izq:
        st.subheader("1. Datos del Pedido y Entrega")
        folio_auto = f"VTA-{datetime.now().strftime('%y%m%d%H%M')}"
        st.caption(f"Folio de Venta: **{folio_auto}**")

        cliente = st.text_input("Nombre del Cliente *", placeholder="Ej. Mariana Torres")
        
        col_t, col_f = st.columns(2)
        with col_t:
            telefono = st.text_input("Teléfono / WhatsApp *", placeholder="10 dígitos (ej. 9811234567)")
        with col_f:
            fecha_entrega = st.date_input("Día programado de entrega *", min_value=date.today())

        col_h, col_d = st.columns(2)
        with col_h:
            horario_entrega = st.text_input("Horario pactado", placeholder="Ej. 4:00 PM a 6:00 PM")
        with col_d:
            direccion = st.text_input("Lugar / Dirección de entrega", placeholder="Ej. Calle 10 #45 o Entrega en local")

        st.divider()
        st.subheader("2. Agregar Productos a la Venta")

        with st.form("form_articulos", clear_on_submit=True):
            prod_nombre = st.text_input("Nombre o descripción del producto")
            col_c, col_p = st.columns(2)
            with col_c:
                prod_cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
            with col_p:
                prod_precio = st.number_input("Precio Unitario ($)", min_value=0.0, step=10.0, format="%.2f")
            
            btn_agregar = st.form_submit_button("➕ Agregar Producto", use_container_width=True)
            if btn_agregar:
                if prod_nombre.strip() and prod_precio > 0:
                    st.session_state.articulos_venta.append({
                        "producto": prod_nombre.strip(),
                        "cantidad": int(prod_cant),
                        "precio_unitario": float(prod_precio),
                        "subtotal": float(prod_cant * prod_precio)
                    })
                    st.rerun()
                else:
                    st.warning("Escribe el nombre del producto y un precio válido mayor a cero.")

    with c_der:
        st.subheader("3. Desglose, Comprobante y Envío")

        if st.session_state.articulos_venta:
            df_partidas = pd.DataFrame(st.session_state.articulos_venta)
            
            st.dataframe(
                df_partidas.rename(columns={
                    "producto": "Producto",
                    "cantidad": "Cant.",
                    "precio_unitario": "P. Unitario",
                    "subtotal": "Subtotal"
                }),
                use_container_width=True,
                hide_index=True
            )

            if st.button("🗑️ Vaciar Lista"):
                st.session_state.articulos_venta = []
                st.rerun()

            total_venta = df_partidas["subtotal"].sum()

            c_tot, c_ant = st.columns(2)
            with c_tot:
                st.metric("Total de la Venta", f"${total_venta:,.2f}")
            with c_ant:
                anticipo = st.number_input("Anticipo recibido ($)", min_value=0.0, max_value=float(total_venta), value=0.0, step=20.0)

            saldo_pendiente = total_venta - anticipo
            
            if saldo_pendiente > 0:
                st.warning(f"⚠️ Saldo pendiente al entregar: **${saldo_pendiente:,.2f}**")
            else:
                st.success("✅ Venta pagada al 100%")

            # Objeto con la información consolidada
            cabecera_datos = {
                "folio": folio_auto,
                "fecha_registro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cliente": cliente.strip(),
                "telefono": telefono.strip(),
                "direccion": direccion.strip() if direccion.strip() else "En sucursal / Mostrador",
                "fecha_entrega": fecha_entrega.strftime("%d/%m/%Y"),
                "horario_entrega": horario_entrega.strip() if horario_entrega.strip() else "Horario a convenir",
                "total": float(total_venta),
                "anticipo": float(anticipo),
                "saldo": float(saldo_pendiente),
                "estado_pago": "Pagado" if saldo_pendiente == 0 else "Saldo Pendiente",
                "estado_entrega": "Pendiente de Entrega"
            }

            # Generación binaria del PDF
            pdf_data = generar_nota_pdf(cabecera_datos, st.session_state.articulos_venta)

            st.divider()

            col_guardar, col_descargar = st.columns(2)
            with col_guardar:
                if st.button("💾 Registrar Venta en el Sistema", type="primary", use_container_width=True):
                    if not cliente.strip() or not telefono.strip():
                        st.error("Es obligatorio capturar nombre y teléfono del cliente.")
                    else:
                        guardar_registro_venta(cabecera_datos, st.session_state.articulos_venta)
                        st.success(f"¡Venta {folio_auto} registrada correctamente!")

            with col_descargar:
                st.download_button(
                    label="📄 Descargar Nota de Entrega (PDF)",
                    data=pdf_data,
                    file_name=f"Nota_Entrega_{folio_auto}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            # Envío automático por WhatsApp
            if telefono.strip():
                clean_tel = "".join(filter(str.isdigit, telefono))
                if len(clean_tel) == 10:
                    clean_tel = f"52{clean_tel}"

                articulos_str = "\n".join([f"• {p['cantidad']}x {p['producto']} (${p['subtotal']:,.2f})" for p in st.session_state.articulos_venta])
                
                texto_wa = (
                    f"¡Hola *{cliente}*! Confirmamos el registro de tu compra:\n\n"
                    f"📄 *Folio:* {folio_auto}\n"
                    f"📦 *Productos vendidos:*\n{articulos_str}\n\n"
                    f"💰 *Total:* ${total_venta:,.2f}\n"
                    f"💵 *Anticipo abonado:* ${anticipo:,.2f}\n"
                    f"⚠️ *Saldo al recibir:* ${saldo_pendiente:,.2f}\n\n"
                    f"📅 *Día pactado de entrega:* {fecha_entrega.strftime('%d/%m/%Y')}\n"
                    f"⏰ *Horario:* {cabecera_datos['horario_entrega']}\n"
                    f"📍 *Punto de entrega:* {cabecera_datos['direccion']}\n\n"
                    f"Te adjuntamos el comprobante formal en PDF. ¡Muchas gracias por tu compra!"
                )
                
                url_wa = f"https://wa.me/{clean_tel}?text={urllib.parse.quote(texto_wa)}"
                st.link_button("📲 Enviar Detalle al Cliente por WhatsApp", url_wa, use_container_width=True)

        else:
            st.info("Agrega los productos en el panel izquierdo para generar el desglose y la nota de entrega.")

# ==================== PESTAÑA 2: HISTORIAL ====================
with tab_consultas:
    st.subheader("Ventas Registradas y Entregas Programadas")
    df_todas = obtener_ventas()
    
    if not df_todas.empty:
        st.dataframe(
            df_todas[["folio", "fecha_registro", "cliente", "telefono", "fecha_entrega", "total", "saldo", "estado_pago"]],
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        folio_sel = st.selectbox("Seleccionar Folio para ver desglose de productos:", df_todas["folio"].tolist())
        if folio_sel:
            detalle_df = obtener_detalle_folio(folio_sel)
            st.write(f"**Partidas del folio {folio_sel}:**")
            st.dataframe(detalle_df, hide_index=True, use_container_width=True)
    else:
        st.write("No hay ventas registradas en la base de datos todavía.")

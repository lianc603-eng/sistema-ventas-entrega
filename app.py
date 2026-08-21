import streamlit as st
import datetime
import uuid
import urllib.parse
import pandas as pd
import pypdfium2 as pdfium
import db
import pdf_nota

st.set_page_config(page_title="Sistema Comercial & Notas", layout="wide", page_icon="⚡")

WHATSAPP_ADMIN = "529817360428"
URL_APP_PUBLICA = "https://sistemaventas1.streamlit.app"
LIMITE_NOTAS_FREE = 5
LIMITE_EMPRENDIMIENTOS_PRO = 4

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None
if "partidas_actuales" not in st.session_state:
    st.session_state.partidas_actuales = []
if "lista_emprendimientos" not in st.session_state:
    st.session_state.lista_emprendimientos = []
if "modo_demo" not in st.session_state:
    st.session_state.modo_demo = False
if "nota_recien_creada" not in st.session_state:
    st.session_state.nota_recien_creada = None

CATALOGO_GIROS = {
    "Estética / Belleza / Uñas / Pestañas / Barbería": {
        "titulo": "COMPROBANTE DE CITA Y SERVICIO",
        "subtitulo": "Estudio de Belleza y Cuidado Personal",
        "etiqueta_fecha": "Fecha de Cita:",
        "etiqueta_lugar": "Sucursal / Cabina:",
        "etiqueta_detalle": "Servicio Realizado",
        "firma_izq": "Atendido por (Especialista)",
        "firma_der": "Clienta / Cliente",
        "color_primario": "#E11D48",
        "color_tabla": "#881337",
        "placeholder_prod": "Ej: Uñas Acrílicas + Retoque de Pestañas"
    },
    "Pastelería / Repostería / Panadería Artesanal": {
        "titulo": "NOTA DE PEDIDO Y REMISIÓN",
        "subtitulo": "Pasteles y Repostería Fina",
        "etiqueta_fecha": "Fecha de Entrega:",
        "etiqueta_lugar": "Lugar de Entrega:",
        "etiqueta_detalle": "Pastel / Postre / Temática",
        "firma_izq": "Chef / Elaborado por",
        "firma_der": "Recibido de Conformidad",
        "color_primario": "#DB2777",
        "color_tabla": "#831843",
        "placeholder_prod": "Ej: Pastel 3 Leches 30 Personas relleno Fresa"
    },
    "Aguas Naturales / Paletería / Bebidas": {
        "titulo": "NOTA DE VENTA Y DESPACHO",
        "subtitulo": "Bebidas y Sabores Naturales",
        "etiqueta_fecha": "Fecha de Surtido:",
        "etiqueta_lugar": "Lugar / Mostrador:",
        "etiqueta_detalle": "Sabor / Litros / Presentación",
        "firma_izq": "Despachado por",
        "firma_der": "Cliente",
        "color_primario": "#059669",
        "color_tabla": "#064E3B",
        "placeholder_prod": "Ej: Vitrolero 20L Horchata de Coco"
    },
    "Agencia de Marketing / Producción": {
        "titulo": "COTIZACIÓN Y ORDEN DE SERVICIO",
        "subtitulo": "Servicios Digitales y Creativos",
        "etiqueta_fecha": "Fecha de Entrega:",
        "etiqueta_lugar": "Modalidad:",
        "etiqueta_detalle": "Entregable / Paquete",
        "firma_izq": "Agencia / Creativo",
        "firma_der": "Aprobación de Cliente",
        "color_primario": "#2563EB",
        "color_tabla": "#0F172A",
        "placeholder_prod": "Ej: Plan de Redes Sociales mensual"
    },
    "Prensa / Reportería / Cobertura": {
        "titulo": "ORDEN DE COBERTURA Y PRENSA",
        "subtitulo": "Servicios Periodísticos y Fotografía",
        "etiqueta_fecha": "Fecha de Evento:",
        "etiqueta_lugar": "Sede / Locación:",
        "etiqueta_detalle": "Cobertura / Servicio",
        "firma_izq": "Reportero Asignado",
        "firma_der": "Aprobación",
        "color_primario": "#DC2626",
        "color_tabla": "#18181B",
        "placeholder_prod": "Ej: Rueda de Prensa + Galería + Nota"
    },
    "Taller Mecánico / Llantera": {
        "titulo": "ORDEN DE SERVICIO AUTOMOTRIZ",
        "subtitulo": "Mantenimiento y Refacciones",
        "etiqueta_fecha": "Fecha Estimada:",
        "etiqueta_lugar": "Vehículo / Placas:",
        "etiqueta_detalle": "Mano de Obra / Refacción",
        "firma_izq": "Mecánico",
        "firma_der": "Autorización Cliente",
        "color_primario": "#D97706",
        "color_tabla": "#451A03",
        "placeholder_prod": "Ej: Afinación Mayor + Cambio de Aceite"
    },
    "Renta de Mobiliario y Eventos": {
        "titulo": "CONTRATO Y REMISIÓN DE MOBILIARIO",
        "subtitulo": "Renta de Equipo y Eventos",
        "etiqueta_fecha": "Fecha del Evento:",
        "etiqueta_lugar": "Dirección del Evento:",
        "etiqueta_detalle": "Artículos en Renta",
        "firma_izq": "Entregado por",
        "firma_der": "Recibido de Conformidad",
        "color_primario": "#7C3AED",
        "color_tabla": "#2E1065",
        "placeholder_prod": "Ej: 5 Mesas Tablón con Mantel + 50 Sillas"
    },
    "Restaurante / Cafetería / Comida": {
        "titulo": "CUENTA DE CONSUMO Y PEDIDO",
        "subtitulo": "Alimentos y Bebidas",
        "etiqueta_fecha": "Fecha de Servicio:",
        "etiqueta_lugar": "Mesa / Para Llevar:",
        "etiqueta_detalle": "Platillo / Consumo",
        "firma_izq": "Atendido por",
        "firma_der": "Cliente",
        "color_primario": "#EA580C",
        "color_tabla": "#431407",
        "placeholder_prod": "Ej: 2 Menús del Día + Bebidas"
    },
    "Comercio General / Tienda": {
        "titulo": "NOTA DE COMPRA Y REMISIÓN",
        "subtitulo": "Venta de Artículos y Productos",
        "etiqueta_fecha": "Fecha:",
        "etiqueta_lugar": "Mostrador / Envío:",
        "etiqueta_detalle": "Artículo / Producto",
        "firma_izq": "Atendió",
        "firma_der": "Cliente",
        "color_primario": "#16A34A",
        "color_tabla": "#14532D",
        "placeholder_prod": "Ej: 3 Paquetes de Productos"
    }
}

u_temp = st.session_state.usuario_activo
es_usuario_admin = bool(u_temp and u_temp.get("rol") == "ADMIN")

if not es_usuario_admin:
    st.markdown("""
    <style>
        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 2rem !important;
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
            }
            .stButton > button {
                width: 100% !important;
                min-height: 48px !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                border-radius: 10px !important;
            }
            input, select, textarea {
                font-size: 16px !important;
            }
        }
        .mobile-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 14px;
        }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# VISTA: ACCESO
# =========================================================
if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>⚡ Generador de Notas & Comprobantes</h2>", unsafe_allow_html=True)
    st.write("")

    col_acc1, col_acc2, col_acc3 = st.columns([1, 1.3, 1])
    with col_acc2:
        if st.button("🚀 Probar Demo Ahora (Sin Registro)", type="primary", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.modo_demo = True
            st.session_state.usuario_activo = {
                "usuario": "demo_prospecto",
                "nombre_comercial": "Mi Negocio",
                "giro": "Estética / Belleza / Uñas / Pestañas / Barbería",
                "telefono": "981 000 0000",
                "rol": "CLIENTE",
                "plan": "TRIAL_PRO",
                "fecha_vencimiento": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "ACTIVA"
            }
            st.session_state.lista_emprendimientos = [{
                "nombre_comercial": "Mi Negocio",
                "giro": "Estética / Belleza / Uñas / Pestañas / Barbería",
                "telefono": "981 000 0000"
            }]
            st.rerun()

        st.markdown("<div style='text-align:center; margin: 12px 0; color: #94A3B8;'>— o accede a tu cuenta —</div>", unsafe_allow_html=True)

        tab_ingresar, tab_crear = st.tabs(["🔑 Iniciar Sesión", "✨ Crear Cuenta"])

        with tab_ingresar:
            usr = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Entrar a mi Sistema", use_container_width=True):
                if usr and pwd:
                    with st.spinner("Validando credenciales..."):
                        res = db.login_usuario(usr.strip(), pwd.strip())
                    if res.get("status") == "success":
                        st.session_state.autenticado = True
                        st.session_state.modo_demo = False
                        st.session_state.usuario_activo = res["user"]
                        st.rerun()
                    else:
                        st.error(res.get("message", "Usuario o contraseña incorrectos."))
                else:
                    st.warning("Escribe tu usuario y contraseña.")

        with tab_crear:
            with st.form("form_reg_simple"):
                r_nom = st.text_input("Nombre de tu Negocio", placeholder="Ej: Nails Studio")
                r_giro = st.selectbox("Giro Comercial", list(CATALOGO_GIROS.keys()))
                r_tel = st.text_input("WhatsApp de Contacto", placeholder="Ej: 9811234567")
                r_usr = st.text_input("Crea un Usuario (sin espacios)", placeholder="Ej: mi_negocio")
                r_pwd = st.text_input("Crea una Contraseña", type="password")
                
                if st.form_submit_button("Crear Cuenta Gratis", type="primary", use_container_width=True):
                    if r_nom and r_usr and r_pwd:
                        with st.spinner("Creando cuenta..."):
                            res_reg = db.registrar_usuario({
                                "usuario": r_usr.strip(),
                                "password": r_pwd.strip(),
                                "nombre_comercial": r_nom.strip(),
                                "giro": r_giro,
                                "telefono": r_tel.strip()
                            })
                        if res_reg.get("status") == "success":
                            st.success("¡Cuenta creada! Inicia sesión en la pestaña izquierda.")
                        else:
                            st.error(res_reg.get("message", "Error al crear cuenta."))
                    else:
                        st.warning("Completa los datos requeridos.")
    st.stop()

# =========================================================
# SESIÓN ACTIVA
# =========================================================
u = st.session_state.usuario_activo
es_admin = (u.get("rol") == "ADMIN")
plan = u.get("plan", "FREE")
es_demo = st.session_state.modo_demo

if not st.session_state.lista_emprendimientos:
    if not es_demo:
        st.session_state.lista_emprendimientos = db.obtener_emprendimientos(u.get("usuario", ""))
    if not st.session_state.lista_emprendimientos:
        st.session_state.lista_emprendimientos = [{
            "nombre_comercial": u.get("nombre_comercial", "Mi Negocio"),
            "giro": u.get("giro", list(CATALOGO_GIROS.keys())[0]),
            "telefono": u.get("telefono", "")
        }]

emprendimientos_usuario = st.session_state.lista_emprendimientos
cfg_guardada = db.obtener_config_pdf(u.get("usuario", "")) if not es_demo else None

# Barra superior
c_top1, c_top2 = st.columns([3.2, 1])
with c_top1:
    if es_admin:
        st.info(f"👑 **Super Administrador:** `{u['usuario']}` · Estudio de Diseño en Vivo Activo")
    elif es_demo:
        st.warning("🚀 **Modo de Prueba** — Estás probando la plataforma.")
    else:
        badge = "🔥 PRO Ilimitado" if plan == "PRO" else f"🌱 Plan Gratuito ({LIMITE_NOTAS_FREE} notas/mes)"
        st.markdown(f"🏢 **{u['nombre_comercial']}** · {badge}")

with c_top2:
    if st.button("🚪 Salir", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario_activo = None
        st.session_state.lista_emprendimientos = []
        st.session_state.modo_demo = False
        st.session_state.nota_recien_creada = None
        st.rerun()

# =========================================================
# MENÚ LATERAL
# =========================================================
with st.sidebar:
    st.header("⚙️ Configuración")
    
    es_pro_o_trial = (plan in ["PRO", "TRIAL_PRO"] or es_admin or es_demo)

    if es_pro_o_trial and len(emprendimientos_usuario) > 1:
        nombres_emp = [e["nombre_comercial"] for e in emprendimientos_usuario]
        emp_sel_nombre = st.selectbox("Marca activa:", nombres_emp)
        emp_activo = next((item for item in emprendimientos_usuario if item["nombre_comercial"] == emp_sel_nombre), emprendimientos_usuario[0])
    else:
        emp_activo = emprendimientos_usuario[0]

    preset = CATALOGO_GIROS.get(emp_activo.get("giro"), list(CATALOGO_GIROS.values())[0])

    negocio_nombre = st.text_input("Nombre de la Marca", value=emp_activo.get("nombre_comercial", ""))
    negocio_contacto = st.text_input("WhatsApp / Teléfono", value=emp_activo.get("telefono", ""))

    if es_pro_o_trial:
        logo_file = st.file_uploader("Logotipo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        logo_bytes = logo_file.getvalue() if logo_file else None
    else:
        st.caption("🔒 *Logotipo disponible en Plan PRO.*")
        logo_bytes = None

    titulo_def = cfg_guardada["titulo"] if cfg_guardada else preset["titulo"]
    subtitulo_def = cfg_guardada["subtitulo"] if cfg_guardada else preset["subtitulo"]
    color_prim_def = cfg_guardada["color_primario"] if cfg_guardada else preset["color_primario"]
    color_tab_def = cfg_guardada["color_tabla"] if cfg_guardada else preset["color_tabla"]
    pie_def = cfg_guardada["mensaje_pie"] if cfg_guardada else "Gracias por su preferencia."
    fuente_def = cfg_guardada.get("fuente_familia", "Helvetica") if cfg_guardada else "Helvetica"

    if es_admin:
        st.markdown("---")
        st.markdown("### 🎛️ Estudio Avanzado de Diseño")
        with st.expander("📝 Textos y Encabezados", expanded=False):
            titulo_doc = st.text_input("Título del Documento", value=titulo_def)
            subtitulo_doc = st.text_input("Subtítulo", value=subtitulo_def)
            mensaje_pie = st.text_area("Leyenda al Pie", value=pie_def)

        with st.expander("🎨 Colores & Tipografía", expanded=False):
            fuente_sel = st.selectbox("Tipografía", ["Helvetica", "Times-Roman", "Courier"], index=0)
            col_primario = st.color_picker("Color de Acento", color_prim_def)
            col_tabla = st.color_picker("Fondo Tabla", color_tab_def)
            simbolo_moneda = st.selectbox("Moneda", ["$", "MXN $", "USD $", "EUR €"])
            desglosar_iva = st.toggle("Activar Desglose de IVA", value=False)
            tasa_iva = 16.0 if desglosar_iva else 0.0
    else:
        titulo_doc = titulo_def
        subtitulo_doc = subtitulo_def
        mensaje_pie = pie_def
        fuente_sel = fuente_def
        col_primario = color_prim_def
        col_tabla = color_tab_def
        simbolo_moneda = "$"
        desglosar_iva = False
        tasa_iva = 0.0

config_pdf_usuario = {
    "fuente_familia": fuente_sel,
    "titulo_documento": titulo_doc,
    "subtitulo_documento": subtitulo_doc,
    "nombre_negocio": negocio_nombre,
    "contacto_negocio": negocio_contacto,
    "mensaje_pie": mensaje_pie,
    "etiqueta_fecha_operativa": preset["etiqueta_fecha"],
    "etiqueta_lugar_operativo": preset["etiqueta_lugar"],
    "etiqueta_detalle": preset["etiqueta_detalle"],
    "firma_izquierda": preset["firma_izq"],
    "firma_derecha": preset["firma_der"],
    "moneda": simbolo_moneda,
    "color_fondo_hoja": "#FFFFFF",
    "color_primario": col_primario,
    "color_tabla_fondo": col_tabla,
    "color_tabla_texto": "#FFFFFF",
    "mostrar_firmas": True,
    "desglosar_iva": desglosar_iva,
    "tasa_iva": tasa_iva,
    "logo_bytes": logo_bytes
}

# =========================================================
# PESTAÑAS
# =========================================================
pestanas_nombres = ["📝 Nueva Nota", "📋 Mis Notas", "🏷️ Catálogo"]
if es_admin:
    pestanas_nombres.append("👑 Panel Admin & Asistencia")

tabs = st.tabs(pestanas_nombres)

# --- PESTAÑA 1: NUEVA NOTA ---
with tabs[0]:
    if st.session_state.nota_recien_creada:
        reciente = st.session_state.nota_recien_creada
        st.success(f"🎉 ¡Nota #{reciente['folio']} creada con éxito!")
        
        tel_limpio = "".join(filter(str.isdigit, reciente["telefono"]))
        if len(tel_limpio) == 10:
            tel_limpio = "52" + tel_limpio
            
        msg_whatsapp = (
            f"¡Hola {reciente['cliente']}! Te comparto tu comprobante de {reciente['negocio']}.\n\n"
            f"📄 *Folio:* {reciente['folio']}\n"
            f"💰 *Total:* ${reciente['total']:,.2f}\n"
            f"💵 *Anticipo:* ${reciente['anticipo']:,.2f}\n"
            f"📌 *Saldo Pendiente:* ${reciente['saldo']:,.2f}\n\n"
            f"¡Muchas gracias por tu preferencia!"
        )
        link_enviar_cliente = f"https://wa.me/{tel_limpio}?text={urllib.parse.quote(msg_whatsapp)}" if tel_limpio else None

        if link_enviar_cliente:
            st.markdown(f"""
            <a href="{link_enviar_cliente}" target="_blank" style="background-color: #25D366; color: white; padding: 14px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 16px; display: block; text-align: center; margin-bottom: 10px;">
                📲 ENVIAR COMPROBANTE POR WHATSAPP
            </a>
            """, unsafe_allow_html=True)

        if st.button("➕ Crear Otra Nota Nueva", type="secondary", use_container_width=True):
            st.session_state.nota_recien_creada = None
            st.session_state.partidas_actuales = []
            st.rerun()

        st.markdown("---")

    if es_admin:
        col_form, col_preview = st.columns([1.15, 0.85])
    else:
        col_form = st.container()
        col_preview = st.container()

    with col_form:
        st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
        st.markdown("### 1️⃣ Datos del Cliente")
        cliente = st.text_input("Nombre del Cliente *", placeholder="Ej: María González")
        telefono = st.text_input("WhatsApp del Cliente (10 dígitos)", placeholder="Ej: 9811234567")
        direccion = st.text_input("Lugar / Sucursal (Opcional)", placeholder="Ej: Cabina 2 / Domicilio")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
        st.markdown("### 2️⃣ Conceptos o Servicios")
        prod_nom = st.text_input("Descripción *", placeholder=preset["placeholder_prod"])
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            prod_cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
        with c_p2:
            prod_precio = st.number_input(f"Precio Unitario ({simbolo_moneda})", min_value=0.0, step=20.0)
            
        if st.button("➕ Agregar a la Nota", use_container_width=True, type="secondary"):
            if prod_nom.strip():
                st.session_state.partidas_actuales.append({
                    "producto": prod_nom.strip(),
                    "cantidad": int(prod_cant),
                    "precio_unitario": float(prod_precio),
                    "subtotal": float(prod_cant * prod_precio)
                })
                st.rerun()

        if st.session_state.partidas_actuales:
            st.table(st.session_state.partidas_actuales)
            if st.button("🗑️ Borrar productos", use_container_width=True):
                st.session_state.partidas_actuales = []
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        partidas_render = st.session_state.partidas_actuales if st.session_state.partidas_actuales else [
            {"producto": f"Muestra: {preset['placeholder_prod']}", "cantidad": 1, "precio_unitario": 0.0, "subtotal": 0.0}
        ]
        total_venta = sum(item["subtotal"] for item in partidas_render)

        st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
        st.markdown("### 3️⃣ Cobro y Saldo")
        fecha_entrega = st.date_input("Fecha", min_value=datetime.date.today())
        anticipo = st.number_input(f"Anticipo Recibido ({simbolo_moneda})", min_value=0.0, step=50.0)

        saldo_pendiente = max(0.0, total_venta - anticipo)
        estado_pago = "Liquidado" if saldo_pendiente == 0.0 else ("Anticipo" if anticipo > 0 else "Pendiente")

        m1, m2, m3 = st.columns(3)
        m1.metric("Total", f"{simbolo_moneda}{total_venta:,.2f}")
        m2.metric("Anticipo", f"{simbolo_moneda}{anticipo:,.2f}")
        m3.metric("Saldo", f"{simbolo_moneda}{saldo_pendiente:,.2f}", delta="- Saldo" if saldo_pendiente > 0 else "Liquidado")
        st.markdown("</div>", unsafe_allow_html=True)

        folio_auto = f"N-{datetime.datetime.now().strftime('%m%d')}-{uuid.uuid4().hex[:3].upper()}"

        if st.button("💾 GENERAR Y GUARDAR COMPROBANTE", type="primary", use_container_width=True):
            if not cliente.strip():
                st.error("⚠️ Escribe el nombre del cliente.")
            elif not st.session_state.partidas_actuales:
                st.error("⚠️ Agrega al menos 1 concepto con el botón ➕.")
            else:
                cabecera_data = {
                    "folio": folio_auto,
                    "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cliente": cliente.strip(),
                    "telefono": telefono.strip() if telefono.strip() else "S/N",
                    "direccion": direccion.strip() if direccion.strip() else "Mostrador",
                    "fecha_entrega": str(fecha_entrega),
                    "horario_entrega": "Horario comercial",
                    "total": total_venta,
                    "anticipo": anticipo,
                    "saldo": saldo_pendiente,
                    "estado_pago": estado_pago,
                    "estado_entrega": "Completado"
                }
                if not es_demo:
                    with st.spinner("Guardando..."):
                        db.guardar_registro_venta(u["usuario"], cabecera_data, st.session_state.partidas_actuales)

                st.session_state.nota_recien_creada = {
                    "folio": folio_auto,
                    "cliente": cliente.strip(),
                    "telefono": telefono.strip(),
                    "total": total_venta,
                    "anticipo": anticipo,
                    "saldo": saldo_pendiente,
                    "negocio": negocio_nombre
                }
                st.rerun()

    with col_preview:
        with st.expander("👁️ Ver Vista Previa del PDF", expanded=es_admin):
            cabecera_preview = {
                "folio": folio_auto,
                "cliente": cliente if cliente.strip() else "Nombre del Cliente",
                "telefono": telefono if telefono.strip() else "981 000 0000",
                "direccion": direccion if direccion.strip() else "Mostrador",
                "fecha_entrega": str(fecha_entrega),
                "horario_entrega": "Entrega",
                "total": total_venta,
                "anticipo": anticipo,
                "saldo": saldo_pendiente
            }
            pdf_bytes_live = pdf_nota.generar_nota_pdf(cabecera_preview, partidas_render, config_personalizada=config_pdf_usuario)
            try:
                pdf_doc = pdfium.PdfDocument(pdf_bytes_live)
                page = pdf_doc.get_page(0)
                bitmap = page.render(scale=1.6)
                st.image(bitmap.to_pil(), use_container_width=True)
            except Exception:
                st.info("💡 PDF listo para descarga.")

            st.download_button(
                label=f"📄 Descargar Archivo PDF ({simbolo_moneda})",
                data=pdf_bytes_live,
                file_name=f"Nota_{folio_auto}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# --- PESTAÑA 2: HISTORIAL ---
with tabs[1]:
    st.subheader("Historial de Notas")
    if not es_demo:
        df_mis_ventas = db.obtener_ventas(u["usuario"], es_admin=False)
        if df_mis_ventas.empty:
            st.info("Aún no tienes notas guardadas.")
        else:
            st.dataframe(df_mis_ventas[["folio", "fecha_registro", "cliente", "telefono", "total", "anticipo", "saldo", "estado_pago"]], use_container_width=True)
            folio_sel = st.selectbox("Selecciona una nota para descargar:", df_mis_ventas["folio"].tolist())
            if folio_sel:
                df_det = db.obtener_detalle_folio(folio_sel)
                fila_c = df_mis_ventas[df_mis_ventas["folio"] == folio_sel].iloc[0].to_dict()
                pdf_reimpreso = pdf_nota.generar_nota_pdf(fila_c, df_det.to_dict(orient="records"), config_personalizada=config_pdf_usuario)
                st.download_button(label=f"📄 Descargar PDF {folio_sel}", data=pdf_reimpreso, file_name=f"Nota_{folio_sel}.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("El historial se activa al registrar tu cuenta.")

# --- PESTAÑA 3: CATÁLOGO ---
with tabs[2]:
    st.subheader("Catálogo de Precios")
    if not es_demo:
        df_cat_ver = db.obtener_productos(u.get("usuario", ""))
        if not df_cat_ver.empty:
            st.dataframe(df_cat_ver[["nombre", "precio_venta"]], use_container_width=True)
    
    with st.form("form_cat_simple"):
        p_nom = st.text_input("Nombre del Servicio o Producto", placeholder="Ej: Uñas Acrílicas")
        p_precio = st.number_input("Precio al Público ($)", min_value=0.0, step=20.0)
            
        if st.form_submit_button("Guardar en Catálogo", use_container_width=True):
            if p_nom.strip():
                if not es_demo:
                    db.guardar_producto(u["usuario"], {"nombre": p_nom.strip(), "costo_base": p_precio, "margen_porcentaje": 0, "precio_venta": p_precio})
                    st.success(f"'{p_nom}' guardado.")
                    st.rerun()

# --- PESTAÑA 4: PANEL ADMIN (ESTUDIO DE DISEÑO EN VIVO LADO A LADO) ---
if es_admin:
    with tabs[3]:
        st.subheader("👑 Panel de Control Maestro & Estudio de Diseño")
        df_usuarios = db.admin_obtener_usuarios()
        if not df_usuarios.empty:
            st.dataframe(df_usuarios, use_container_width=True)
            st.markdown("---")
            
            lista_clientes = [usr for usr in df_usuarios["usuario"].tolist() if usr != u["usuario"]]
            if not lista_clientes:
                lista_clientes = df_usuarios["usuario"].tolist()
                
            cliente_seleccionado = st.selectbox("🎯 Selecciona un Cliente para Asistencia:", lista_clientes)
            info_cliente = df_usuarios[df_usuarios["usuario"] == cliente_seleccionado].iloc[0].to_dict()

            tab_diseno_remoto, tab_lic, tab_cat_remoto = st.tabs([
                "🎨 Estudio de Diseño en Vivo (100% Personalizado)",
                "🔑 Licencia y Suscripción", 
                "🏷️ Cargar Catálogo al Cliente"
            ])

            # SUB-TAB 1: ESTUDIO DE DISEÑO LADO A LADO EN VIVO
            with tab_diseno_remoto:
                st.markdown(f"### 🎨 Estudio de Diseño Oficial: `{info_cliente.get('nombre_comercial')}` ({cliente_seleccionado})")
                
                cfg_actual_cliente = db.obtener_config_pdf(cliente_seleccionado)
                preset_cliente = CATALOGO_GIROS.get(info_cliente.get("giro"), list(CATALOGO_GIROS.values())[0])

                col_controles, col_preview_live = st.columns([1.1, 0.9])

                with col_controles:
                    with st.expander("📝 1. Textos y Encabezados del Comprobante", expanded=True):
                        e_titulo = st.text_input("Título Principal", value=cfg_actual_cliente["titulo"] if cfg_actual_cliente else preset_cliente["titulo"], key="e_tit")
                        e_subtitulo = st.text_input("Subtítulo de la Marca", value=cfg_actual_cliente["subtitulo"] if cfg_actual_cliente else preset_cliente["subtitulo"], key="e_sub")
                        e_pie = st.text_area("Leyenda / Condiciones al Pie", value=cfg_actual_cliente["mensaje_pie"] if cfg_actual_cliente else "Gracias por su preferencia. Citas con 50% de anticipo.", key="e_pie")

                    with st.expander("🏷️ 2. Etiquetas y Firmas de Conformidad", expanded=True):
                        e_fecha = st.text_input("Etiqueta Fecha", value=cfg_actual_cliente.get("etiqueta_fecha", preset_cliente["etiqueta_fecha"]) if cfg_actual_cliente else preset_cliente["etiqueta_fecha"], key="e_fec")
                        e_lugar = st.text_input("Etiqueta Lugar/Cabina", value=cfg_actual_cliente.get("etiqueta_lugar", preset_cliente["etiqueta_lugar"]) if cfg_actual_cliente else preset_cliente["etiqueta_lugar"], key="e_lug")
                        e_detalle = st.text_input("Etiqueta de Tabla", value=cfg_actual_cliente.get("etiqueta_detalle", preset_cliente["etiqueta_detalle"]) if cfg_actual_cliente else preset_cliente["etiqueta_detalle"], key="e_det")
                        
                        c_fir1, c_fir2 = st.columns(2)
                        with c_fir1:
                            e_fir_izq = st.text_input("Firma Izquierda", value=preset_cliente["firma_izq"], key="e_fizq")
                        with c_fir2:
                            e_fir_der = st.text_input("Firma Derecha", value=preset_cliente["firma_der"], key="e_fder")

                    with st.expander("🎨 3. Colores de Identidad & Tipografía", expanded=True):
                        e_fuente = st.selectbox("Familia Tipográfica", ["Helvetica", "Times-Roman", "Courier"], index=0, key="e_fnt")
                        
                        c_col1, c_col2 = st.columns(2)
                        with c_col1:
                            e_color_prim = st.color_picker("Color Principal / Acento", cfg_actual_cliente["color_primario"] if cfg_actual_cliente else preset_cliente["color_primario"], key="e_cp")
                        with c_col2:
                            e_color_tab = st.color_picker("Fondo Encabezado Tabla", cfg_actual_cliente["color_tabla"] if cfg_actual_cliente else preset_cliente["color_tabla"], key="e_ct")

                    with st.expander("🖼️ 4. Logotipo & Desglose de Impuestos", expanded=True):
                        e_logo = st.file_uploader("Subir Logotipo del Cliente (PNG/JPG)", type=["png", "jpg", "jpeg"], key="e_logo_file")
                        e_logo_bytes = e_logo.getvalue() if e_logo else None
                        
                        e_iva = st.toggle("Activar Desglose de IVA en comprobantes", value=False, key="e_iva_tgl")
                        e_tasa = st.number_input("Tasa IVA (%)", min_value=0.0, value=16.0, key="e_tasa_num") if e_iva else 0.0

                    if st.button("💾 GUARDAR PLANTILLA AL CLIENTE", type="primary", use_container_width=True):
                        db.guardar_config_pdf(cliente_seleccionado, {
                            "titulo": e_titulo,
                            "subtitulo": e_subtitulo,
                            "color_primario": e_color_prim,
                            "color_tabla": e_color_tab,
                            "mensaje_pie": e_pie,
                            "fuente_familia": e_fuente,
                            "etiqueta_fecha": e_fecha,
                            "etiqueta_lugar": e_lugar,
                            "etiqueta_detalle": e_detalle
                        })
                        st.success(f"¡Plantilla 100% personalizada y guardada para {cliente_seleccionado}!")

                # COLUMNA DERECHA: RENDERIZADO EN TIEMPO REAL
                with col_preview_live:
                    st.markdown("#### 👁️ Vista Previa en Vivo del PDF")
                    
                    config_render_live = {
                        "fuente_familia": e_fuente,
                        "titulo_documento": e_titulo,
                        "subtitulo_documento": e_subtitulo,
                        "nombre_negocio": info_cliente.get("nombre_comercial", "Marca"),
                        "contacto_negocio": info_cliente.get("telefono", "981 000 0000"),
                        "mensaje_pie": e_pie,
                        "etiqueta_fecha_operativa": e_fecha,
                        "etiqueta_lugar_operativo": e_lugar,
                        "etiqueta_detalle": e_detalle,
                        "firma_izquierda": e_fir_izq,
                        "firma_derecha": e_fir_der,
                        "moneda": "$",
                        "color_fondo_hoja": "#FFFFFF",
                        "color_primario": e_color_prim,
                        "color_tabla_fondo": e_color_tab,
                        "color_tabla_texto": "#FFFFFF",
                        "mostrar_firmas": True,
                        "desglosar_iva": e_iva,
                        "tasa_iva": e_tasa,
                        "logo_bytes": e_logo_bytes
                    }
                    
                    cabecera_demo = {
                        "folio": "DEMO-001",
                        "cliente": "María González (Muestra)",
                        "telefono": "981 123 4567",
                        "direccion": "Sucursal Principal / Cabina",
                        "fecha_entrega": str(datetime.date.today()),
                        "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total": 650.0,
                        "anticipo": 200.0,
                        "saldo": 450.0
                    }
                    partidas_demo = [
                        {"producto": f"Servicio: {preset_cliente['placeholder_prod']}", "cantidad": 1, "precio_unitario": 450.0, "subtotal": 450.0},
                        {"producto": "Mantenimiento / Aplicación adicional", "cantidad": 1, "precio_unitario": 200.0, "subtotal": 200.0}
                    ]

                    pdf_bytes_cliente_live = pdf_nota.generar_nota_pdf(cabecera_demo, partidas_demo, config_personalizada=config_render_live)
                    
                    try:
                        pdf_doc_live = pdfium.PdfDocument(pdf_bytes_cliente_live)
                        page_l = pdf_doc_live.get_page(0)
                        bitmap_l = page_l.render(scale=1.8)
                        st.image(bitmap_l.to_pil(), caption="Vista previa en tiempo real", use_container_width=True)
                    except Exception:
                        st.info("💡 Cambia los colores y textos a la izquierda.")

            # SUB-TAB 2: LICENCIA
            with tab_lic:
                st.markdown(f"**Gestionando:** `{cliente_seleccionado}` | Plan actual: **{info_cliente.get('plan')}**")
                c_u2, c_u3 = st.columns(2)
                with c_u2:
                    nuevo_plan = st.selectbox("Plan Asignado:", ["PRO", "FREE"], key="plan_adm")
                with c_u3:
                    dias_extender = st.number_input("Sumar Días (Mes = 30):", min_value=0, value=30, step=30, key="dias_adm")
                    
                if st.button("💾 Actualizar Suscripción del Cliente", type="primary"):
                    db.admin_actualizar_plan_suscripcion(cliente_seleccionado, "CLIENTE", nuevo_plan, dias_extender, "ACTIVA")
                    st.success(f"¡Suscripción de {cliente_seleccionado} actualizada!")
                    st.rerun()

            # SUB-TAB 3: CATÁLOGO
            with tab_cat_remoto:
                st.markdown(f"**Catálogo de:** `{info_cliente.get('nombre_comercial')}`")
                df_cat_cliente = db.obtener_productos(cliente_seleccionado)
                if not df_cat_cliente.empty:
                    st.dataframe(df_cat_cliente[["nombre", "precio_venta"]], use_container_width=True)
                else:
                    st.caption("El cliente aún no tiene productos registrados.")

                with st.form("form_add_prod_remoto"):
                    c_np1, c_np2 = st.columns([3, 1])
                    with c_np1:
                        np_nom = st.text_input("Nombre del Servicio / Producto", placeholder="Ej: Uñas Esculturales")
                    with c_np2:
                        np_pre = st.number_input("Precio al Público ($)", min_value=0.0, step=20.0)

                    if st.form_submit_button("💾 Agregar Producto a la Cuenta del Cliente"):
                        if np_nom.strip():
                            db.guardar_producto(cliente_seleccionado, {
                                "nombre": np_nom.strip(),
                                "costo_base": np_pre,
                                "margen_porcentaje": 0,
                                "precio_venta": np_pre
                            })
                            st.success(f"¡'{np_nom}' agregado al catálogo de {cliente_seleccionado}!")
                            st.rerun()

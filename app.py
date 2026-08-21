import streamlit as st
import datetime
import uuid
import urllib.parse
import pandas as pd
import db
import pdf_nota

# Configuración base
st.set_page_config(page_title="Sistema Comercial & Notas", layout="wide", page_icon="⚡")

# Configuración comercial y enlaces
WHATSAPP_ADMIN = "529817360428"
URL_APP_PUBLICA = "https://sistemaventas1.streamlit.app"
LIMITE_NOTAS_FREE = 5
LIMITE_EMPRENDIMIENTOS_PRO = 4

# Inicialización de estado en sesión
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

# =========================================================
# MOTOR DE ESTILOS: MÓVIL PARA CLIENTES / DESKTOP PARA TI
# =========================================================
u_temp = st.session_state.usuario_activo
es_usuario_admin = (u_temp and u_temp.get("rol") == "ADMIN")

if not es_usuario_admin:
    # Inyección de estilos móviles para smartphones
    st.markdown("""
    <style>
        /* Optimización Touch para Celulares */
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
                margin-top: 6px !important;
                margin-bottom: 6px !important;
            }
            input, select, textarea {
                font-size: 16px !important; /* Evita zoom automático en iPhone */
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 6px;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 8px 12px !important;
                font-size: 14px !important;
            }
            [data-testid="stMetricValue"] {
                font-size: 1.4rem !important;
            }
        }
        /* Tarjetas limpias en móvil */
        .mobile-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 14px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Estilos limpios para Desktop / Laptop
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
        }
        .stButton > button {
            border-radius: 6px !important;
            font-weight: 600 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# VISTA: ACCESO AMIGABLE Y DIRECTO
# =========================================================
if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>⚡ Generador de Notas & Comprobantes</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 15px;'>Crea notas y cotizaciones profesionales en PDF listas para enviar por WhatsApp.</p>", unsafe_allow_html=True)
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

        st.markdown("<div style='text-align:center; margin: 12px 0; color: #94A3B8; font-size: 14px;'>— o accede a tu cuenta —</div>", unsafe_allow_html=True)

        tab_ingresar, tab_crear = st.tabs(["🔑 Iniciar Sesión", "✨ Crear Cuenta"])

        with tab_ingresar:
            usr = st.text_input("Usuario o Correo")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Entrar a mi Sistema", use_container_width=True, type="secondary"):
                with st.spinner("Validando..."):
                    res = db.login_usuario(usr, pwd)
                if res.get("status") == "success":
                    st.session_state.autenticado = True
                    st.session_state.modo_demo = False
                    st.session_state.usuario_activo = res["user"]
                    st.session_state.lista_emprendimientos = db.obtener_emprendimientos(res["user"]["usuario"])
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        with tab_crear:
            with st.form("form_reg_simple"):
                r_nom = st.text_input("Nombre de tu Negocio / Marca", placeholder="Ej: Nails Studio / Postres Lili")
                r_giro = st.selectbox("Giro Comercial", list(CATALOGO_GIROS.keys()))
                r_tel = st.text_input("WhatsApp de Contacto", placeholder="Ej: 9811234567")
                r_usr = st.text_input("Crea un Usuario (sin espacios)", placeholder="Ej: mi_negocio")
                r_pwd = st.text_input("Crea una Contraseña", type="password")
                
                if st.form_submit_button("Crear Cuenta Gratis (1 Día PRO)", type="primary", use_container_width=True):
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
# GESTIÓN DE SESIÓN
# =========================================================
u = st.session_state.usuario_activo
es_admin = (u.get("rol") == "ADMIN")
plan = u.get("plan", "FREE")
es_demo = st.session_state.modo_demo

emprendimientos_usuario = st.session_state.lista_emprendimientos
if not emprendimientos_usuario:
    emprendimientos_usuario = [{
        "nombre_comercial": u.get("nombre_comercial", "Mi Negocio"),
        "giro": u.get("giro", list(CATALOGO_GIROS.keys())[0]),
        "telefono": u.get("telefono", "")
    }]

# Barra superior
c_top1, c_top2 = st.columns([3.2, 1])
with c_top1:
    if es_admin:
        st.info(f"👑 **Super Administrador:** `{u['usuario']}` · Modo Desktop & Estudio Avanzado Activo")
    elif es_demo:
        st.warning("🚀 **Modo de Prueba** — Estás probando la plataforma en tu dispositivo.")
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

# Banner amigable para usuarios FREE
if plan == "FREE" and not es_admin and not es_demo:
    msg_up = f"Hola, soy {u.get('usuario')}. Quiero activar el Plan PRO ($199 MXN) y cotizar el servicio de personalización oficial de mi marca."
    link_wsp_upgrade = f"https://wa.me/{WHATSAPP_ADMIN}?text={urllib.parse.quote(msg_up)}"
    st.markdown(f"""
    <div style="background-color: #FEF3C7; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; display: flex; flex-direction: column; gap: 6px;">
        <span style="color: #92400E; font-size: 13px; font-weight: 600;">⭐ <b>Plan Gratuito:</b> {LIMITE_NOTAS_FREE} notas al mes.</span>
        <span style="color: #B45309; font-size: 12px;">¿Quieres notas ilimitadas o que personalicemos la plantilla con tu logotipo?</span>
        <a href="{link_wsp_upgrade}" target="_blank" style="background-color: #25D366; color: white; padding: 8px 12px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 13px; text-align: center; display: inline-block;">
            💬 Activar Plan PRO ($199 MXN)
        </a>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# MENÚ LATERAL: COMPLETO EN LAPTOP / SIMPLE EN MÓVIL
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

    # Si eres Admin en laptop: Todas las herramientas desplegadas
    if es_admin:
        st.markdown("---")
        st.markdown("### 🎛️ Estudio Avanzado de Diseño")
        
        with st.expander("📝 Textos y Encabezados", expanded=True):
            titulo_doc = st.text_input("Título del Documento", value=preset["titulo"])
            subtitulo_doc = st.text_input("Subtítulo", value=preset["subtitulo"])
            lbl_fecha = st.text_input("Etiqueta Fecha", value=preset["etiqueta_fecha"])
            lbl_lugar = st.text_input("Etiqueta Lugar/Sucursal", value=preset["etiqueta_lugar"])
            lbl_detalle = st.text_input("Etiqueta Tabla", value=preset["etiqueta_detalle"])
            mensaje_pie = st.text_area("Leyenda al Pie", value="Gracias por su preferencia. Favor de verificar sus servicios/productos.")

        with st.expander("🎨 Paleta de Colores Hexadecimal", expanded=True):
            col_fondo = st.color_picker("Fondo de la Hoja", "#FFFFFF")
            col_primario = st.color_picker("Color de Acento / Franja", preset["color_primario"])
            col_tabla = st.color_picker("Fondo Encabezado Tabla", preset["color_tabla"])
            col_texto_tabla = st.color_picker("Texto Encabezado Tabla", "#FFFFFF")

        with st.expander("💲 Moneda e Impuestos", expanded=True):
            simbolo_moneda = st.selectbox("Moneda", ["$", "MXN $", "USD $", "EUR €"])
            desglosar_iva = st.toggle("Activar Desglose de IVA", value=False)
            tasa_iva = st.number_input("Tasa IVA (%)", min_value=0.0, value=16.0) if desglosar_iva else 0.0

        with st.expander("✍️ Firmas de Conformidad", expanded=True):
            mostrar_firmas = st.checkbox("Incluir bloque de firmas", value=True)
            firma_izq = st.text_input("Firma Izquierda", value=preset["firma_izq"])
            firma_der = st.text_input("Firma Derecha", value=preset["firma_der"])

    # Si es cliente en móvil: opciones limpias y discretas
    else:
        with st.expander("🛠️ Personalización Opcional", expanded=False):
            titulo_doc = st.text_input("Título", value=preset["titulo"])
            simbolo_moneda = st.selectbox("Moneda", ["$", "MXN $", "USD $", "EUR €"])
            col_primario = st.color_picker("Color de acento", preset["color_primario"])
            mensaje_pie = st.text_area("Leyenda al pie", value="Favor de revisar sus productos/servicios.")
            desglosar_iva = st.toggle("Desglosar IVA (16%)", value=False) if es_pro_o_trial else False
            tasa_iva = 16.0 if desglosar_iva else 0.0

        subtitulo_doc = preset["subtitulo"]
        lbl_fecha = preset["etiqueta_fecha"]
        lbl_lugar = preset["etiqueta_lugar"]
        lbl_detalle = preset["etiqueta_detalle"]
        col_fondo = "#FFFFFF"
        col_tabla = preset["color_tabla"]
        col_texto_tabla = "#FFFFFF"
        mostrar_firmas = True
        firma_izq = preset["firma_izq"]
        firma_der = preset["firma_der"]

    if es_pro_o_trial and len(emprendimientos_usuario) < LIMITE_EMPRENDIMIENTOS_PRO and not es_demo:
        with st.expander("➕ Agregar otra marca (Hasta 4)", expanded=False):
            with st.form("form_nueva_marca"):
                m_nom = st.text_input("Nombre de la nueva marca")
                m_giro = st.selectbox("Giro", list(CATALOGO_GIROS.keys()))
                m_tel = st.text_input("WhatsApp")
                if st.form_submit_button("Guardar Marca"):
                    if m_nom.strip():
                        db.guardar_emprendimiento(u["usuario"], {"nombre_comercial": m_nom.strip(), "giro": m_giro, "telefono": m_tel.strip()})
                        st.session_state.lista_emprendimientos = db.obtener_emprendimientos(u["usuario"])
                        st.rerun()

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
# PESTAÑAS PRINCIPALES
# =========================================================
pestanas_nombres = ["📝 Nueva Nota", "📋 Mis Notas", "🏷️ Precios"]
if es_admin:
    pestanas_nombres.append("👑 Panel Admin & Estudio")

tabs = st.tabs(pestanas_nombres)

# ---------------------------------------------------------
# PESTAÑA 1: CREAR NOTA (ADAPTADA 100% PARA MÓVIL)
# ---------------------------------------------------------
with tabs[0]:
    df_propias = db.obtener_ventas(u["usuario"], es_admin=False) if not es_demo else pd.DataFrame()
    cant_emitidas = len(df_propias)

    if plan == "FREE" and not es_admin and not es_demo and cant_emitidas >= LIMITE_NOTAS_FREE:
        st.error(f"⚠️ Has alcanzado el límite de {LIMITE_NOTAS_FREE} notas este mes en tu Plan Gratuito.")
        st.info("Para seguir creando notas ilimitadas, activa tu Plan PRO por solo $199 MXN.")
        st.stop()

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

    # En Desktop para Admin: Vista 2 Columnas / En Móvil para Clientes: Flujo Vertical Fluido
    if es_admin:
        col_form, col_preview = st.columns([1.15, 0.85])
    else:
        col_form = st.container()
        col_preview = st.container()

    with col_form:
        # PASO 1: DATOS CLIENTE
        st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
        st.markdown("### 1️⃣ Datos del Cliente")
        cliente = st.text_input("Nombre del Cliente *", placeholder="Ej: María González")
        telefono = st.text_input("WhatsApp del Cliente (10 dígitos)", placeholder="Ej: 9811234567")
        direccion = st.text_input("Lugar / Sucursal (Opcional)", placeholder="Ej: Cabina 2 / Domicilio")
        st.markdown("</div>", unsafe_allow_html=True)

        # PASO 2: CONCEPTOS
        st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
        st.markdown("### 2️⃣ ¿Qué vendiste o qué servicio realizaste?")
        prod_nom = st.text_input("Descripción del Servicio/Producto *", placeholder=preset["placeholder_prod"])
        
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
            if st.button("🗑️ Borrar lista de productos", use_container_width=True):
                st.session_state.partidas_actuales = []
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        partidas_render = st.session_state.partidas_actuales if st.session_state.partidas_actuales else [
            {"producto": f"Muestra: {preset['placeholder_prod']}", "cantidad": 1, "precio_unitario": 0.0, "subtotal": 0.0}
        ]

        total_venta = sum(item["subtotal"] for item in partidas_render)

        # PASO 3: COBRO Y SALDO
        st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
        st.markdown("### 3️⃣ Cobro y Saldo")
        fecha_entrega = st.date_input("Fecha de Servicio / Entrega", min_value=datetime.date.today())
        anticipo = st.number_input(f"Anticipo o Adelanto Recibido ({simbolo_moneda})", min_value=0.0, step=50.0)

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
                st.error("⚠️ Por favor escribe el nombre del cliente.")
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
                    with st.spinner("Guardando en la nube..."):
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
                "folio": folio_auto if 'folio_auto' in locals() else "N-001",
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
                import pypdfium2 as pdfium
                pdf_doc = pdfium.PdfDocument(pdf_bytes_live)
                page = pdf_doc.get_page(0)
                bitmap = page.render(scale=1.6)
                st.image(bitmap.to_pil(), use_container_width=True)
            except Exception:
                st.info("💡 Cambia los datos y descarga el PDF.")

            st.download_button(
                label=f"📄 Descargar Archivo PDF ({simbolo_moneda})",
                data=pdf_bytes_live,
                file_name=f"Nota_{folio_auto}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ---------------------------------------------------------
# PESTAÑA 2: MIS NOTAS
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("Historial de Notas")
    if not es_demo:
        df_mis_ventas = db.obtener_ventas(u["usuario"], es_admin=False)
        if df_mis_ventas.empty:
            st.info("Aún no tienes notas guardadas.")
        else:
            st.dataframe(df_mis_ventas[["folio", "fecha_registro", "cliente", "telefono", "total", "anticipo", "saldo", "estado_pago"]], use_container_width=True)
            st.markdown("---")
            
            folio_sel = st.selectbox("Selecciona una nota para descargar:", df_mis_ventas["folio"].tolist())
            if folio_sel:
                df_det = db.obtener_detalle_folio(folio_sel)
                fila_c = df_mis_ventas[df_mis_ventas["folio"] == folio_sel].iloc[0].to_dict()
                pdf_reimpreso = pdf_nota.generar_nota_pdf(fila_c, df_det.to_dict(orient="records"), config_personalizada=config_pdf_usuario)
                st.download_button(label=f"📄 Descargar PDF {folio_sel}", data=pdf_reimpreso, file_name=f"Nota_{folio_sel}.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("El historial se activa al registrar tu cuenta.")

# ---------------------------------------------------------
# PESTAÑA 3: PRECIOS
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("Catálogo de Precios")
    with st.form("form_cat_simple"):
        p_nom = st.text_input("Nombre del Servicio o Producto", placeholder="Ej: Uñas Acrílicas / Pastel 3 Leches")
        p_precio = st.number_input("Precio al Público ($)", min_value=0.0, step=20.0)
            
        if st.form_submit_button("Guardar en Catálogo", use_container_width=True):
            if p_nom.strip():
                if not es_demo:
                    db.guardar_producto(u["usuario"], {"nombre": p_nom.strip(), "costo_base": p_precio, "margen_porcentaje": 0, "precio_venta": p_precio})
                    st.success(f"'{p_nom}' guardado.")
                else:
                    st.info("Guardado en modo demo.")

# ---------------------------------------------------------
# PESTAÑA 4: PANEL ADMIN (SOLO PARA TI EN TU LAPTOP)
# ---------------------------------------------------------
if es_admin:
    with tabs[3]:
        st.subheader("👑 Panel Maestro de Control & Estudio de Diseño")
        
        # Compartir enlace por WhatsApp
        msg_prospecto = f"¡Hola! Te comparto este generador de notas y comprobantes en PDF para tu negocio. Puedes probarlo gratis aquí: {URL_APP_PUBLICA}"
        link_wsp_share = f"https://wa.me/?text={urllib.parse.quote(msg_prospecto)}"
        st.markdown(f"""
        <a href="{link_wsp_share}" target="_blank" style="background-color: #25D366; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-bottom: 15px;">
            📲 Compartir Enlace a un Prospecto por WhatsApp
        </a>
        """, unsafe_allow_html=True)

        df_usuarios = db.admin_obtener_usuarios()
        if not df_usuarios.empty:
            st.dataframe(df_usuarios, use_container_width=True)
            st.markdown("---")
            
            # Control de Licencias
            st.markdown("### 🔑 Activar o Renovar Suscripciones")
            c_u1, c_u2, c_u3 = st.columns(3)
            with c_u1:
                u_elegido = st.selectbox("Usuario a gestionar:", df_usuarios["usuario"].tolist())
            with c_u2:
                nuevo_plan = st.selectbox("Plan:", ["PRO", "FREE"])
            with c_u3:
                dias_extender = st.number_input("Sumar Días (Mes = 30):", min_value=0, value=30, step=30)
                
            if st.button("💾 Guardar Licencia del Cliente", type="primary"):
                db.admin_actualizar_plan_suscripcion(u_elegido, "CLIENTE", nuevo_plan, dias_extender, "ACTIVA")
                st.success(f"¡Suscripción de {u_elegido} actualizada!")
                st.rerun()

            st.markdown("---")
            # Servicio de Personalización
            st.markdown("### 🎨 Servicio Extra: Personalizar Plantilla para un Cliente")
            st.caption("Cobro sugerido: $300 - $800 MXN por dejar el sistema llave en mano.")
            
            with st.form("form_servicio_personalizacion"):
                st.markdown(f"**Personalizando para el usuario:** `{u_elegido}`")
                p_c1, p_c2 = st.columns(2)
                with p_c1:
                    cust_nombre = st.text_input("Nombre Oficial de la Marca", placeholder="Ej: Bella Studio & Nails")
                    cust_tel = st.text_input("WhatsApp de la Marca", placeholder="Ej: 981 123 4567")
                    cust_giro = st.selectbox("Giro Comercial", list(CATALOGO_GIROS.keys()))
                with p_c2:
                    st.info("💡 Este cambio actualizará el negocio del cliente para que cuando él inicie sesión en su teléfono, ya tenga todo listo.")

                if st.form_submit_button("🎨 Guardar Identidad al Cliente", type="primary"):
                    if cust_nombre.strip():
                        db.guardar_emprendimiento(u_elegido, {
                            "nombre_comercial": cust_nombre.strip(),
                            "giro": cust_giro,
                            "telefono": cust_tel.strip()
                        })
                        st.success(f"¡Identidad guardada para {u_elegido}!")
                    else:
                        st.error("Ingresa el nombre de la marca.")

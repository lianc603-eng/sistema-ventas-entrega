import streamlit as st
import datetime
import uuid
import urllib.parse
import pandas as pd
import db
import pdf_nota

st.set_page_config(page_title="Plataforma Comercial Multi-Giro", layout="wide", page_icon="⚡")

# Configuración comercial
WHATSAPP_ADMIN = "529817360428"  # Tu WhatsApp para activaciones y propuestas
URL_APP_PUBLICA = "https://sistemaventas1.streamlit.app"
LIMITE_NOTAS_FREE = 5             # Límite ajustado a 5 notas al mes para el Plan FREE
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

CATALOGO_GIROS = {
    # Belleza, Uñas, Pestañas, Cejas y Barbería
    "Estética / Belleza / Uñas / Pestañas / Barbería": {
        "titulo": "COMPROBANTE DE CITA Y SERVICIOS DE BELLEZA",
        "subtitulo": "Estudio de Belleza, Cuidado Personal y Estilismo",
        "etiqueta_fecha": "FECHA DE LA CITA / SERVICIO:",
        "etiqueta_lugar": "Sucursal / Cabina / Domicilio:",
        "etiqueta_detalle": "Servicio (Uñas / Pestañas / Corte / Tinte / Cejas)",
        "firma_izq": "Atendido por (Especialista / Estilista)",
        "firma_der": "Conformidad de la Clienta / Cliente",
        "color_primario": "#E11D48",
        "color_tabla": "#881337",
        "placeholder_prod": "Ej: Uñas Acrílicas + Lifting de Pestañas + Planchado de Cejas"
    },
    "Pastelería / Repostería / Panadería Artesanal": {
        "titulo": "NOTA DE PEDIDO Y REMISIÓN DE REPOSTERÍA",
        "subtitulo": "Pasteles de Diseño, Postres y Repostería Fina",
        "etiqueta_fecha": "FECHA DE ENTREGA DEL PEDIDO:",
        "etiqueta_lugar": "Lugar de Entrega / Mostrador:",
        "etiqueta_detalle": "Pastel / Postre / Porciones / Temática",
        "firma_izq": "Elaborado por (Chef Pastelero/a)",
        "firma_der": "Recibido de Conformidad (Cliente)",
        "color_primario": "#DB2777",
        "color_tabla": "#831843",
        "placeholder_prod": "Ej: Pastel 3 Leches 30 personas relleno de fresa"
    },
    "Aguas Naturales / Paletería / Bebidas Artesanales": {
        "titulo": "NOTA DE VENTA Y DESPACHO DE BEBIDAS",
        "subtitulo": "Preparación de Aguas Naturales y Sabores Artesanales",
        "etiqueta_fecha": "FECHA DE SURTIDO / EVENTO:",
        "etiqueta_lugar": "Lugar de Entrega / Mostrador:",
        "etiqueta_detalle": "Sabor / Vitrolero / Litros / Presentación",
        "firma_izq": "Despachado por (Encargado/a)",
        "firma_der": "Recibido de Conformidad (Cliente)",
        "color_primario": "#059669",
        "color_tabla": "#064E3B",
        "placeholder_prod": "Ej: Vitrolero 20L Horchata de Coco"
    },
    "Prensa / Reportería / Cobertura Periodística": {
        "titulo": "ORDEN DE COBERTURA Y COMISIONES DE PRENSA",
        "subtitulo": "Servicios Periodísticos, Fotografía y Redacción",
        "etiqueta_fecha": "FECHA DE COBERTURA / EVENTO:",
        "etiqueta_lugar": "Sede / Locación de Rueda de Prensa:",
        "etiqueta_detalle": "Servicio Periodístico / Nota / Reportaje",
        "firma_izq": "Reportero(a) Asignado",
        "firma_der": "Aprobación de Cobertura y Medio",
        "color_primario": "#DC2626",
        "color_tabla": "#18181B",
        "placeholder_prod": "Ej: Cobertura Conferencia + Nota Informativa"
    },
    "Agencia de Marketing / Producción Audiovisual": {
        "titulo": "COTIZACIÓN Y ORDEN DE SERVICIO CREATIVO",
        "subtitulo": "Marketing Digital, Campañas y Producción",
        "etiqueta_fecha": "FECHA DE ENTREGA / PRODUCCIÓN:",
        "etiqueta_lugar": "Modalidad (Online / Locación):",
        "etiqueta_detalle": "Entregable / Paquete de Campaña / Video",
        "firma_izq": "Director Creativo / Agencia",
        "firma_der": "Aceptación de Presupuesto (Cliente)",
        "color_primario": "#2563EB",
        "color_tabla": "#0F172A",
        "placeholder_prod": "Ej: Gestión de Redes Sociales mensual"
    },
    "Taller Mecánico / Refaccionaria / Llantera": {
        "titulo": "ORDEN DE SERVICIO Y DIAGNÓSTICO",
        "subtitulo": "Mantenimiento Preventivo, Correctivo y Refacciones",
        "etiqueta_fecha": "FECHA ESTIMADA DE SALIDA:",
        "etiqueta_lugar": "Datos del Vehículo / Placas:",
        "etiqueta_detalle": "Refacción / Mano de Obra / Afinación",
        "firma_izq": "Mecánico Responsable",
        "firma_der": "Autorización de Trabajo y Retiro",
        "color_primario": "#D97706",
        "color_tabla": "#451A03",
        "placeholder_prod": "Ej: Afinación Mayor + Cambio de Aceite"
    },
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
        "placeholder_prod": "Ej: 5 Mesas Tablón con Mantel + 50 Sillas"
    },
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
        "placeholder_prod": "Ej: 3 Menús Ejecutivos del Día"
    },
    "Imprenta / Serigrafía / Rotulación": {
        "titulo": "ORDEN DE PRODUCCIÓN GRÁFICA Y REPARTO",
        "subtitulo": "Impresión Offset, Digital y Gran Formato",
        "etiqueta_fecha": "FECHA COMPROMISO DE ENTREGA:",
        "etiqueta_lugar": "Lugar de Entrega / Mostrador:",
        "etiqueta_detalle": "Especificación de Impresión / Millar",
        "firma_izq": "Prensista / Taller Gráfico",
        "firma_der": "Visto Bueno y Recepción de Trabajo",
        "color_primario": "#0284C7",
        "color_tabla": "#082F49",
        "placeholder_prod": "Ej: 1,000 Volantes 1/4 carta couche"
    },
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
        "placeholder_prod": "Ej: 10 Bultos de Cemento Gris"
    },
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
        "placeholder_prod": "Ej: Caja de Huevo 12kg + Aceite 1L"
    },
    "Escuela / Kínder / Guardería / Academia": {
        "titulo": "RECIBO DE PAGO DE COLEGIATURA Y TALLERES",
        "subtitulo": "Servicios Educativos y Estancia Infantil",
        "etiqueta_fecha": "FECHA DE PAGO / MES:",
        "etiqueta_lugar": "Plantel / Grado y Grupo:",
        "etiqueta_detalle": "Concepto (Inscripción / Colegiatura)",
        "firma_izq": "Administración Escolar",
        "firma_der": "Padre / Tutor",
        "color_primario": "#2563EB",
        "color_tabla": "#1E3A8A",
        "placeholder_prod": "Ej: Colegiatura del Mes - Nivel Preescolar"
    },
    "Consultoría / Honorarios / Despacho": {
        "titulo": "RECIBO DE HONORARIOS Y ASESORÍA",
        "subtitulo": "Servicios Profesionales de Asesoría",
        "etiqueta_fecha": "FECHA DE EMISIÓN:",
        "etiqueta_lugar": "Modalidad (Oficina / Remoto):",
        "etiqueta_detalle": "Concepto de Honorarios / Horas de Sesión",
        "firma_izq": "Consultor(a) Titular",
        "firma_der": "Aceptación de Servicios (Cliente)",
        "color_primario": "#334155",
        "color_tabla": "#0F172A",
        "placeholder_prod": "Ej: Auditoría y planeación administrativa"
    }
}

# =========================================================
# VISTA: ACCESO, REGISTRO GOOGLE Y MODO DEMO
# =========================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>⚡ Sistema Comercial Multi-Giro & Generador de Notas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 17px;'>Genera comprobantes de venta, órdenes de servicio y notas personalizadas en PDF para cualquier tipo de negocio.</p>", unsafe_allow_html=True)
    st.write("")

    col_demo1, col_demo2, col_demo3 = st.columns([1, 1.4, 1])
    with col_demo2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%); border: 1px solid #C7D2FE; border-radius: 10px; padding: 14px 18px; text-align: center; margin-bottom: 20px;">
            <span style="font-size: 16px; font-weight: bold; color: #3730A3;">✨ ¿Quieres probar el sistema ahora mismo?</span><br>
            <span style="font-size: 13px; color: #4338CA;">Prueba todas las funciones en modo interactivo sin crear cuenta.</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Probar Demo Interactivo Ahora", type="secondary", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.modo_demo = True
            st.session_state.usuario_activo = {
                "usuario": "demo_prospecto",
                "nombre_comercial": "Mi Negocio Demo",
                "giro": "Estética / Belleza / Uñas / Pestañas / Barbería",
                "telefono": "981 000 0000",
                "rol": "CLIENTE",
                "plan": "TRIAL_PRO",
                "fecha_vencimiento": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "ACTIVA"
            }
            st.session_state.lista_emprendimientos = [{
                "nombre_comercial": "Mi Negocio Demo",
                "giro": "Estética / Belleza / Uñas / Pestañas / Barbería",
                "telefono": "981 000 0000"
            }]
            st.rerun()

        st.markdown("---")
        
        tab_login, tab_google, tab_registro = st.tabs([
            "🔑 Iniciar Sesión", 
            "🌐 Acceso Rápido con Google", 
            "🚀 Crear Cuenta (1 Día PRO Gratis)"
        ])

        with tab_login:
            usr = st.text_input("Usuario o Correo")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Ingresar a mi Cuenta", type="primary", use_container_width=True):
                with st.spinner("Validando en la nube..."):
                    res = db.login_usuario(usr, pwd)
                if res.get("status") == "success":
                    st.session_state.autenticado = True
                    st.session_state.modo_demo = False
                    st.session_state.usuario_activo = res["user"]
                    st.session_state.lista_emprendimientos = db.obtener_emprendimientos(res["user"]["usuario"])
                    st.rerun()
                else:
                    st.error(res.get("message", "Usuario o contraseña inválidos."))

        with tab_google:
            st.markdown("#### ⚡ Acceso con un Clic con tu Cuenta Google")
            st.caption("Ingresa tu correo de Google y nombre de negocio para comenzar tu prueba PRO de 24 horas.")
            
            with st.form("form_google_auth"):
                g_email = st.text_input("Tu Correo de Google", placeholder="ejemplo@gmail.com")
                g_nom = st.text_input("Nombre de tu Emprendimiento", placeholder="Ej: Nails & Lashes Studio")
                g_giro = st.selectbox("Giro Comercial", list(CATALOGO_GIROS.keys()), key="giro_google")
                
                if st.form_submit_button("🔴 Continuar con Google (Prueba PRO 24h)", type="primary", use_container_width=True):
                    if g_email.strip() and "@" in g_email and g_nom.strip():
                        user_id = g_email.split("@")[0].lower()
                        pwd_auto = "google_auth_pass"
                        
                        with st.spinner("Conectando con Google Sheets..."):
                            res_login = db.login_usuario(user_id, pwd_auto)
                            if res_login.get("status") == "success":
                                st.session_state.autenticado = True
                                st.session_state.usuario_activo = res_login["user"]
                                st.session_state.lista_emprendimientos = db.obtener_emprendimientos(user_id)
                                st.rerun()
                            else:
                                res_reg = db.registrar_google({
                                    "usuario": user_id,
                                    "password": pwd_auto,
                                    "nombre_comercial": g_nom.strip(),
                                    "giro": g_giro,
                                    "telefono": g_email
                                })
                                if res_reg.get("status") == "success":
                                    st.session_state.autenticado = True
                                    st.session_state.usuario_activo = res_reg["user"]
                                    st.session_state.lista_emprendimientos = [{
                                        "nombre_comercial": g_nom.strip(),
                                        "giro": g_giro,
                                        "telefono": g_email
                                    }]
                                    st.rerun()
                                else:
                                    st.error(res_reg.get("message", "Error al conectar."))
                    else:
                        st.error("Ingresa un correo de Google válido y el nombre de tu marca.")

        with tab_registro:
            st.info("🎁 **Al registrarte obtienes Acceso Total PRO por 1 día** (Subida de logo, múltiples marcas, desglose de IVA y notas ilimitadas). Al vencer, conservas tu Plan FREE con 5 notas al mes.")
            with st.form("form_auto_registro"):
                r_nom = st.text_input("Nombre de tu Emprendimiento", placeholder="Ej: Studio Belleza & Spa")
                r_giro = st.selectbox("Giro Comercial", list(CATALOGO_GIROS.keys()), key="giro_reg")
                r_tel = st.text_input("WhatsApp de Contacto", placeholder="Ej: 981 123 4567")
                r_usr = st.text_input("Usuario deseado (sin espacios)")
                r_pwd = st.text_input("Contraseña", type="password")
                
                if st.form_submit_button("Crear Cuenta y Activar Prueba PRO (1 Día)", type="primary", use_container_width=True):
                    if r_nom and r_usr and r_pwd:
                        with st.spinner("Activando tu prueba PRO..."):
                            res_reg = db.registrar_usuario({
                                "usuario": r_usr.strip(),
                                "password": r_pwd.strip(),
                                "nombre_comercial": r_nom.strip(),
                                "giro": r_giro,
                                "telefono": r_tel.strip()
                            })
                        if res_reg.get("status") == "success":
                            st.success("¡Cuenta activada con 1 día de prueba PRO! Inicia sesión en la pestaña izquierda.")
                        else:
                            st.error(res_reg.get("message", "Error al crear cuenta."))
                    else:
                        st.error("Por favor completa los campos requeridos.")
    st.stop()

# =========================================================
# GESTIÓN DE SESIÓN ACTIVA Y ROLES
# =========================================================
u = st.session_state.usuario_activo
es_admin = (u.get("rol") == "ADMIN")
plan = u.get("plan", "FREE")
es_demo = st.session_state.modo_demo

emprendimientos_usuario = st.session_state.lista_emprendimientos
if not emprendimientos_usuario:
    emprendimientos_usuario = [{
        "nombre_comercial": u.get("nombre_comercial", "Mi Emprendimiento"),
        "giro": u.get("giro", list(CATALOGO_GIROS.keys())[0]),
        "telefono": u.get("telefono", "")
    }]

# Barra superior de estado
c_top1, c_top2 = st.columns([3, 1])
with c_top1:
    if es_admin:
        st.info(f"👑 **Super Administrador:** `{u['usuario']}` | **Acceso Ilimitado Total** | Gestión de Licencias Activa")
    elif es_demo:
        st.warning("🚀 **Modo Demo Interactivo** — Estás probando la versión PRO. Crea tu cuenta para guardar datos.")
    else:
        if plan == "PRO":
            badge_plan = "🔥 Plan PRO (Ilimitado - 4 Marcas)"
        elif plan == "TRIAL_PRO":
            badge_plan = "⏳ Prueba PRO (24 Horas)"
        else:
            badge_plan = f"🌱 Plan FREE ({LIMITE_NOTAS_FREE} notas/mes)"
            
        color_st = "green" if u.get("estado") == "ACTIVA" else "red"
        st.markdown(f"🏢 **{u['nombre_comercial']}** | {badge_plan} | Estado: :{color_st}[**{u.get('estado', 'ACTIVA')}**]")

with c_top2:
    if st.button("🚪 Cerrar Sesión / Salir", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario_activo = None
        st.session_state.lista_emprendimientos = []
        st.session_state.modo_demo = False
        st.rerun()

# =========================================================
# BANNER UPGRADE A PRO PARA CUENTAS FREE
# =========================================================
if plan == "FREE" and not es_admin and not es_demo:
    mensaje_wsp = f"¡Hola! Soy {u.get('usuario')} ({u.get('nombre_comercial')}). Me interesa activar el Plan PRO ($199 MXN) para tener notas ilimitadas, subir mi logo y registrar mis 4 emprendimientos."
    link_wsp = f"https://wa.me/{WHATSAPP_ADMIN}?text={urllib.parse.quote(mensaje_wsp)}"
    
    st.markdown(f"""
    <div style="background-color: #FEF3C7; border: 1px solid #F59E0B; border-radius: 8px; padding: 12px 18px; margin-bottom: 15px;">
        <span style="font-size: 15px; font-weight: 600; color: #92400E;">⭐ Estás en el Plan Gratuito (Límite: {LIMITE_NOTAS_FREE} notas al mes)</span><br>
        <span style="font-size: 13px; color: #B45309;">¿Necesitas emitir notas ilimitadas, colocar tu logotipo y registrar hasta 4 marcas?</span>
        <div style="margin-top: 8px;">
            <a href="{link_wsp}" target="_blank" style="background-color: #25D366; color: white; padding: 6px 14px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px; display: inline-block;">
                💬 Contactar por WhatsApp para Activar Plan PRO ($199 MXN)
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# CANAL DE FEEDBACK Y PROPUESTAS DE MEJORA
# =========================================================
with st.expander("💬 ¿Tienes alguna propuesta de mejora, duda o sugerencia? Escríbenos aquí", expanded=False):
    col_fb1, col_fb2 = st.columns([1.2, 0.8])
    with col_fb1:
        with st.form("form_feedback_usuario"):
            tipo_propuesta = st.selectbox("Tipo de Mensaje", ["💡 Propuesta de Nueva Función", "🎨 Sugerencia de Diseño", "❓ Duda / Soporte Técnico", "🤝 Consulta Comercial"])
            comentario_propuesta = st.text_area("Describe tu propuesta o comentario:")
            contacto_propuesta = st.text_input("WhatsApp o Correo de contacto", value=u.get("telefono", ""))
            
            if st.form_submit_button("Enviar Propuesta"):
                if comentario_propuesta.strip():
                    with st.spinner("Enviando comentario..."):
                        db.guardar_feedback(u.get("usuario", "demo"), {
                            "tipo": tipo_propuesta,
                            "comentario": comentario_propuesta.strip(),
                            "contacto": contacto_propuesta.strip()
                        })
                    st.success("¡Gracias por tu mensaje! Tu sugerencia ha sido enviada al desarrollador.")
                else:
                    st.warning("Por favor escribe tu propuesta antes de enviar.")
    
    with col_fb2:
        msg_directo = f"Hola, soy {u.get('usuario')} ({u.get('nombre_comercial')}) y tengo una propuesta de mejora para el sistema."
        link_fb_directo = f"https://wa.me/{WHATSAPP_ADMIN}?text={urllib.parse.quote(msg_directo)}"
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; text-align: center;">
            <span style="font-weight: bold; color: #1E293B;">¿Prefieres hablar directamente?</span><br>
            <span style="font-size: 13px; color: #64748B;">Atención directa por WhatsApp con el desarrollador.</span><br><br>
            <a href="{link_fb_directo}" target="_blank" style="background-color: #25D366; color: white; padding: 6px 14px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px; display: inline-block;">
                📱 Chat Directo por WhatsApp
            </a>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# MENÚ LATERAL: DISEÑO Y MARCAS
# =========================================================
with st.sidebar:
    st.header("🏢 Emprendimiento Activo")
    
    es_pro_o_trial = (plan in ["PRO", "TRIAL_PRO"] or es_admin or es_demo)

    if es_pro_o_trial and len(emprendimientos_usuario) > 1:
        nombres_emp = [e["nombre_comercial"] for e in emprendimientos_usuario]
        emp_sel_nombre = st.selectbox("Selecciona la marca a emitir:", nombres_emp)
        emp_activo = next((item for item in emprendimientos_usuario if item["nombre_comercial"] == emp_sel_nombre), emprendimientos_usuario[0])
    else:
        emp_activo = emprendimientos_usuario[0]

    if es_pro_o_trial and len(emprendimientos_usuario) < LIMITE_EMPRENDIMIENTOS_PRO and not es_demo:
        with st.expander("➕ Dar de alta otra marca", expanded=False):
            with st.form("form_add_emp"):
                add_nom = st.text_input("Nombre de la nueva marca")
                add_giro = st.selectbox("Giro comercial", list(CATALOGO_GIROS.keys()), key="add_giro_key")
                add_tel = st.text_input("WhatsApp / Contacto")
                if st.form_submit_button("Guardar Marca"):
                    if add_nom.strip():
                        db.guardar_emprendimiento(u["usuario"], {
                            "nombre_comercial": add_nom.strip(),
                            "giro": add_giro,
                            "telefono": add_tel.strip()
                        })
                        st.session_state.lista_emprendimientos = db.obtener_emprendimientos(u["usuario"])
                        st.success(f"¡Marca '{add_nom}' registrada!")
                        st.rerun()

    preset = CATALOGO_GIROS.get(emp_activo.get("giro"), list(CATALOGO_GIROS.values())[0])

    st.markdown("---")
    st.header("🎨 Personalización del PDF")

    with st.expander("🏢 Identidad de Marca", expanded=True):
        negocio_nombre = st.text_input("Nombre de la Marca", value=emp_activo.get("nombre_comercial", ""))
        negocio_contacto = st.text_input("WhatsApp / Contacto", value=emp_activo.get("telefono", ""))
        
        if es_pro_o_trial:
            logo_file = st.file_uploader("Subir Logotipo (PNG/JPG)", type=["png", "jpg", "jpeg"])
            logo_bytes = logo_file.getvalue() if logo_file else None
        else:
            st.caption("🔒 *Logotipo exclusivo para Plan PRO.*")
            logo_bytes = None

    with st.expander("📝 Textos del Documento", expanded=False):
        titulo_doc = st.text_input("Título", value=preset["titulo"])
        subtitulo_doc = st.text_input("Subtítulo", value=preset["subtitulo"])
        lbl_fecha = st.text_input("Etiqueta Fecha", value=preset["etiqueta_fecha"])
        lbl_lugar = st.text_input("Etiqueta Lugar", value=preset["etiqueta_lugar"])
        lbl_detalle = st.text_input("Etiqueta Tabla", value=preset["etiqueta_detalle"])
        mensaje_pie = st.text_area("Pie de página", value="Favor de verificar sus servicios al momento de la entrega.")

    with st.expander("🎨 Colores de Marca", expanded=False):
        col_fondo = st.color_picker("Fondo hoja", "#FFFFFF")
        col_primario = st.color_picker("Acento", preset["color_primario"])
        col_tabla = st.color_picker("Fondo tabla", preset["color_tabla"])
        col_texto_tabla = st.color_picker("Texto tabla", "#FFFFFF")

    with st.expander("💲 Moneda e Impuestos (IVA)", expanded=True):
        simbolo_moneda = st.selectbox("Moneda", ["$", "MXN $", "USD $", "EUR €"])
        if es_pro_o_trial:
            desglosar_iva = st.toggle("Activar Desglose de IVA / Impuesto", value=False)
            tasa_iva = st.number_input("Tasa IVA (%)", min_value=0.0, value=16.0) if desglosar_iva else 0.0
        else:
            st.caption("🔒 *Desglose de IVA disponible en Plan PRO.*")
            desglosar_iva = False
            tasa_iva = 0.0

    with st.expander("✍️ Firmas de Conformidad", expanded=False):
        mostrar_firmas = st.checkbox("Firmas de conformidad", value=True)
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
# PESTAÑAS PRINCIPALES
# =========================================================
titulos_tabs = ["📝 Nueva Venta & Preview", "🏷️ Catálogo", "📊 Historial en Google Sheets"]
if es_admin:
    titulos_tabs.append("👑 Panel de Suscripciones & Compartir")

tabs = st.tabs(titulos_tabs)

# --- PESTAÑA 1: NUEVA VENTA & PREVIEW ---
with tabs[0]:
    df_propias = db.obtener_ventas(u["usuario"], es_admin=False) if not es_demo else pd.DataFrame()
    cant_emitidas = len(df_propias)
    
    # Verificación de límite de 5 notas en Plan FREE
    if plan == "FREE" and not es_admin and not es_demo and cant_emitidas >= LIMITE_NOTAS_FREE:
        st.warning(f"⚠️ Has alcanzado el límite de **{LIMITE_NOTAS_FREE} comprobantes** del Plan FREE.")
        msg_limite = f"¡Hola! Soy {u.get('usuario')}. Alcancé mi límite de {LIMITE_NOTAS_FREE} notas mensuales en el Plan FREE y quiero activar el Plan PRO ($199 MXN)."
        link_limite = f"https://wa.me/{WHATSAPP_ADMIN}?text={urllib.parse.quote(msg_limite)}"
        st.markdown(f"""
        <div style="margin-top: 10px;">
            <a href="{link_limite}" target="_blank" style="background-color: #25D366; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                🚀 Activar Plan PRO Ilimitado por WhatsApp
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_izq, col_der = st.columns([1.1, 0.9])
        with col_izq:
            st.subheader(f"1. Datos de Venta ({negocio_nombre})")
            if plan == "FREE" and not es_admin and not es_demo:
                st.caption(f"Comprobantes usados este mes: **{cant_emitidas}/{LIMITE_NOTAS_FREE}** (Plan FREE)")

            f1, f2 = st.columns(2)
            with f1:
                folio_auto = f"DOC-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                folio = st.text_input("Folio / ID", value=folio_auto)
                cliente = st.text_input("Nombre del Cliente", placeholder="Ej: María González")
                telefono = st.text_input("Teléfono / WhatsApp", placeholder="Ej: 981 123 4567")
                direccion = st.text_area(lbl_lugar.replace(":", ""), placeholder="Ej: Sucursal Centro / Domicilio")

            with f2:
                fecha_entrega = st.date_input(lbl_fecha.replace(":", ""), min_value=datetime.date.today())
                tipo_horario = st.selectbox("Horario", ["Hora específica", "Rango predefinido", "Horario abierto"])
                if tipo_horario == "Hora específica":
                    hora_sel = st.time_input("Hora", value=datetime.time(12, 0))
                    horario_entrega = hora_sel.strftime("%I:%M %p").lstrip("0")
                elif tipo_horario == "Rango predefinido":
                    horario_entrega = st.selectbox("Rango", ["09:00 - 12:00", "12:00 - 15:00", "15:00 - 18:00", "18:00 - 21:00"])
                else:
                    horario_entrega = "Horario abierto"

                anticipo = st.number_input(f"Anticipo Pagado ({simbolo_moneda})", min_value=0.0, step=50.0)
                estado_entrega = st.selectbox("Estado", ["Pendiente / Por Entregar", "En Proceso / Ruta", "Completado / Entregado", "Cancelado"])

            st.markdown("---")
            st.subheader("2. Conceptos o Servicios")
            cp1, cp2, cp3, cp4 = st.columns([3, 1, 1, 1])
            with cp1:
                prod_nom = st.text_input("Descripción", placeholder=preset["placeholder_prod"])
            with cp2:
                prod_cant = st.number_input("Cant.", min_value=1, value=1, step=1)
            with cp3:
                prod_precio = st.number_input(f"P. Unit ({simbolo_moneda})", min_value=0.0, step=10.0)
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
                    if st.button("💾 Guardar y Sincronizar a Google Sheets", type="primary", use_container_width=True):
                        if not cliente.strip():
                            st.error("Por favor ingresa el nombre del cliente.")
                        elif es_demo:
                            st.info("💡 En Modo Demo no se guardan registros en Google Sheets. ¡Crea tu cuenta gratis para sincronizar!")
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
                            with st.spinner("Guardando en Google Sheets..."):
                                db.guardar_registro_venta(u["usuario"], cabecera_data, st.session_state.partidas_actuales)
                            st.session_state.partidas_actuales = []
                            st.success(f"¡Venta {folio} guardada en tu Google Sheet!")
                            st.rerun()

                with btn_limpiar:
                    if st.button("🗑️ Limpiar", use_container_width=True):
                        st.session_state.partidas_actuales = []
                        st.rerun()

        with col_der:
            st.subheader("👁️ Vista Previa en Vivo")
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
                st.image(pil_image, caption=f"Emprendimiento: {negocio_nombre}", use_container_width=True)
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
with tabs[1]:
    st.subheader(f"Catálogo de Precios ({negocio_nombre})")
    with st.form("form_cat"):
        p_nom = st.text_input("Nombre del Concepto / Servicio")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_costo = st.number_input("Costo Base ($)", min_value=0.0, step=10.0)
        with c2:
            p_margen = st.number_input("Margen (%)", min_value=0.0, value=35.0)
        with c3:
            p_precio = st.number_input("Precio al Público ($)", value=float(p_costo * (1 + p_margen/100)))
        
        if st.form_submit_button("Guardar en Catálogo"):
            if p_nom.strip():
                if not es_demo:
                    with st.spinner("Guardando en catálogo..."):
                        db.guardar_producto(u["usuario"], {
                            "nombre": p_nom.strip(),
                            "costo_base": p_costo,
                            "margen_porcentaje": p_margen,
                            "precio_venta": p_precio
                        })
                    st.success("Guardado en Google Sheets.")
                else:
                    st.info("¡Producto de prueba configurado exitosamente!")
            else:
                st.error("Ingresa el nombre del producto.")

# --- PESTAÑA 3: HISTORIAL ---
with tabs[2]:
    st.subheader("Historial de Comprobantes Registrados")
    if not es_demo:
        df_mis_ventas = db.obtener_ventas(u["usuario"], es_admin=False)
        if df_mis_ventas.empty:
            st.info("No tienes ventas registradas aún.")
        else:
            st.dataframe(df_mis_ventas, use_container_width=True)
            st.markdown("---")
            folio_sel = st.selectbox("Reimprimir Folio:", df_mis_ventas["folio"].tolist())
            if folio_sel:
                df_det = db.obtener_detalle_folio(folio_sel)
                st.table(df_det)
                fila_c = df_mis_ventas[df_mis_ventas["folio"] == folio_sel].iloc[0].to_dict()
                partidas_l = df_det.to_dict(orient="records")
                pdf_rep = pdf_nota.generar_nota_pdf(fila_c, partidas_l, config_personalizada=config_pdf_usuario)
                st.download_button(label=f"📄 Descargar PDF {folio_sel}", data=pdf_rep, file_name=f"Nota_{folio_sel}.pdf", mime="application/pdf")
    else:
        st.info("El historial de base de datos se activa al registrar tu cuenta gratuita.")

# --- PESTAÑA 4: PANEL ADMINISTRADOR & COMPARTIR ---
if es_admin:
    with tabs[3]:
        st.subheader("👑 Panel Maestro de Control & Herramientas de Cierre")
        
        st.markdown("### 📤 Compartir la Plataforma con Clientes Potenciales")
        c_sh1, c_sh2 = st.columns(2)
        with c_sh1:
            st.text_input("Enlace público de tu aplicación para prospectos:", value=URL_APP_PUBLICA)
        with c_sh2:
            msg_prospecto = f"¡Hola! Te comparto este generador de notas y comprobantes en PDF para tu negocio. Puedes probarlo gratis aquí: {URL_APP_PUBLICA}"
            link_compartir_wsp = f"https://wa.me/?text={urllib.parse.quote(msg_prospecto)}"
            st.write("")
            st.markdown(f"""
            <a href="{link_compartir_wsp}" target="_blank" style="background-color: #25D366; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                📲 Compartir Enlace por WhatsApp a un Prospecto
            </a>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 👥 Control de Usuarios y Licencias")
        df_usuarios = db.admin_obtener_usuarios()
        
        if not df_usuarios.empty:
            st.dataframe(df_usuarios, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Modificar Plan o Activar Suscripción")
            
            c_adm1, c_adm2, c_adm3, c_adm4 = st.columns(4)
            with c_adm1:
                u_elegido = st.selectbox("Usuario a gestionar", df_usuarios["usuario"].tolist())
            with c_adm2:
                nuevo_plan = st.selectbox("Plan Asignado", ["PRO", "TRIAL_PRO", "FREE"])
            with c_adm3:
                nuevo_rol = st.selectbox("Rol de Acceso", ["CLIENTE", "ADMIN"])
            with c_adm4:
                dias_extender = st.number_input("Extender Suscripción (Mes = 30 días)", min_value=0, value=30, step=30)
                
            nuevo_estado = st.selectbox("Estado de Cuenta", ["ACTIVA", "SUSPENDIDA"])

            if st.button("💾 Guardar y Aplicar Cambios en Google Sheets", type="primary"):
                with st.spinner("Actualizando en Google Sheets..."):
                    db.admin_actualizar_plan_suscripcion(u_elegido, nuevo_rol, nuevo_plan, dias_extender, nuevo_estado)
                st.success(f"Usuario '{u_elegido}' actualizado exitosamente.")
                st.rerun()
        else:
            st.info("No hay usuarios registrados aún.")

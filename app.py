import streamlit as st
import datetime
import uuid
import db
import pdf_nota

st.set_page_config(page_title="Plataforma Comercial Multi-Giro", layout="wide", page_icon="⚡")

ADMIN_PASSWORD = "admin2026"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None
if "partidas_actuales" not in st.session_state:
    st.session_state.partidas_actuales = []

CATALOGO_GIROS = {
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
        "placeholder_prod": "Ej: Pastel 3 Leches 30 personas"
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
# PANTALLA DE ACCESO Y REGISTRO
# =========================================================
if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>⚡ Acceso & Registro de Emprendedores</h2>", unsafe_allow_html=True)
    st.write("")
    
    col_c1, col_c2, col_c3 = st.columns([1, 1.3, 1])
    with col_c2:
        tab_login, tab_registro, tab_admin = st.tabs(["🔑 Iniciar Sesión", "🚀 Registrar mi Emprendimiento", "👑 Admin"])
        
        with tab_login:
            usr = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", type="primary", use_container_width=True):
                with st.spinner("Validando en la nube..."):
                    res = db.login_usuario(usr, pwd)
                if res.get("status") == "success":
                    st.session_state.autenticado = True
                    st.session_state.es_admin = False
                    st.session_state.usuario_activo = res["user"]
                    st.rerun()
                else:
                    st.error(res.get("message", "Credenciales incorrectas."))

        with tab_registro:
            st.info("🎁 **Crea tu cuenta hoy y obtén 30 días de prueba gratuita.**")
            with st.form("form_auto_registro"):
                r_nom = st.text_input("Nombre de tu Emprendimiento / Marca", placeholder="Ej: Aguas La Guadalupana")
                r_giro = st.selectbox("Giro de tu Negocio", list(CATALOGO_GIROS.keys()))
                r_tel = st.text_input("WhatsApp / Teléfono", placeholder="Ej: 981 123 4567")
                r_usr = st.text_input("Nombre de Usuario deseado (sin espacios)")
                r_pwd = st.text_input("Crea una Contraseña", type="password")
                
                if st.form_submit_button("Crear Cuenta y Comenzar", type="primary", use_container_width=True):
                    if r_nom and r_usr and r_pwd:
                        with st.spinner("Creando cuenta en Google Sheets..."):
                            res_reg = db.registrar_usuario({
                                "usuario": r_usr.strip(),
                                "password": r_pwd.strip(),
                                "nombre_comercial": r_nom.strip(),
                                "giro": r_giro,
                                "telefono": r_tel.strip()
                            })
                        if res_reg.get("status") == "success":
                            st.success("¡Cuenta creada exitosamente! Ve a la pestaña 'Iniciar Sesión'.")
                        else:
                            st.error(res_reg.get("message", "Error al crear cuenta."))
                    else:
                        st.error("Por favor completa los campos obligatorios.")

        with tab_admin:
            clave_admin = st.text_input("Clave Maestra", type="password")
            if st.button("Entrar como Administrador", use_container_width=True):
                if clave_admin == ADMIN_PASSWORD:
                    st.session_state.autenticado = True
                    st.session_state.es_admin = True
                    st.session_state.usuario_activo = {"usuario": "admin", "nombre_comercial": "Master Admin"}
                    st.rerun()
                else:
                    st.error("Clave maestra incorrecta.")
    st.stop()

# =========================================================
# HEADER Y LOGOUT
# =========================================================
c_top1, c_top2 = st.columns([3, 1])
with c_top1:
    if st.session_state.es_admin:
        st.info("👑 **Panel Maestro de Administración** — Conectado a Google Sheets")
    else:
        u = st.session_state.usuario_activo
        color = "green" if u.get("estado") == "ACTIVA" else "red"
        st.markdown(f"🏢 **{u['nombre_comercial']}** ({u['giro']}) | Estado: :{color}[**{u.get('estado', 'ACTIVA')}**] | Vence: `{u.get('fecha_vencimiento')}`")

with c_top2:
    if st.button("🚪 Salir", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.es_admin = False
        st.session_state.usuario_activo = None
        st.rerun()

# =========================================================
# MÓDULO ADMINISTRADOR
# =========================================================
if st.session_state.es_admin:
    st.title("⚙️ Gestión de Emprendimientos y Suscripciones")
    tab_adm_negocios, tab_adm_ventas = st.tabs(["👥 Emprendedores Registrados", "📊 Ventas Globales"])
    
    with tab_adm_negocios:
        df_neg = db.admin_obtener_negocios()
        st.dataframe(df_neg, use_container_width=True)
        
        if not df_neg.empty:
            st.subheader("Renovar o Suspender Cliente")
            c1, c2, c3 = st.columns(3)
            with c1:
                sel_u = st.selectbox("Seleccionar Emprendimiento", df_neg["usuario"].tolist())
            with c2:
                dias_add = st.number_input("Extender Suscripción (Días)", min_value=0, value=30, step=30)
            with c3:
                st_act = st.selectbox("Estado", ["ACTIVA", "SUSPENDIDA"])
            
            if st.button("Guardar Cambios en Google Sheets", type="primary"):
                with st.spinner("Actualizando..."):
                    db.admin_actualizar_suscripcion(sel_u, dias_add, st_act)
                st.success("Suscripción actualizada.")
                st.rerun()

    with tab_adm_ventas:
        df_todas = db.obtener_ventas(usuario_activo="admin", es_admin=True)
        if not df_todas.empty:
            st.metric("Total Facturado en la Plataforma", f"${df_todas['total'].sum():,.2f}")
            st.dataframe(df_todas, use_container_width=True)
        else:
            st.info("Sin registros globales aún.")
    st.stop()

# =========================================================
# MÓDULO EMPRENDEDOR / CLIENTE
# =========================================================
u_activo = st.session_state.usuario_activo

if u_activo.get("estado") == "SUSPENDIDA":
    st.error("⚠️ **Tu suscripción mensual está vencida.**")
    st.warning("Comunícate con el administrador para renovar tu acceso mensual.")
    st.stop()

with st.sidebar:
    st.header("🎨 Diseño de Comprobante")
    preset = CATALOGO_GIROS.get(u_activo.get("giro"), list(CATALOGO_GIROS.values())[0])

    with st.expander("🏢 Identidad de Marca", expanded=True):
        negocio_nombre = st.text_input("Nombre de la Marca", value=u_activo.get("nombre_comercial", ""))
        negocio_contacto = st.text_input("WhatsApp / Contacto", value=u_activo.get("telefono", ""))
        logo_file = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        logo_bytes = logo_file.getvalue() if logo_file else None

    with st.expander("📝 Textos", expanded=False):
        titulo_doc = st.text_input("Título", value=preset["titulo"])
        subtitulo_doc = st.text_input("Subtítulo", value=preset["subtitulo"])
        lbl_fecha = st.text_input("Etiqueta Fecha", value=preset["etiqueta_fecha"])
        lbl_lugar = st.text_input("Etiqueta Lugar", value=preset["etiqueta_lugar"])
        lbl_detalle = st.text_input("Etiqueta Tabla", value=preset["etiqueta_detalle"])
        mensaje_pie = st.text_area("Pie de página", value="Favor de verificar sus productos al momento de la entrega.")

    with st.expander("🎨 Colores", expanded=False):
        col_fondo = st.color_picker("Fondo hoja", "#FFFFFF")
        col_primario = st.color_picker("Acento", preset["color_primario"])
        col_tabla = st.color_picker("Fondo tabla", preset["color_tabla"])
        col_texto_tabla = st.color_picker("Texto tabla", "#FFFFFF")

    with st.expander("💲 Moneda e Impuestos (IVA)", expanded=True):
        simbolo_moneda = st.selectbox("Moneda", ["$", "MXN $", "USD $", "EUR €"])
        desglosar_iva = st.toggle("Activar Desglose de IVA", value=False)
        tasa_iva = st.number_input("Tasa IVA (%)", min_value=0.0, value=16.0) if desglosar_iva else 0.0

    with st.expander("✍️ Firmas", expanded=False):
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

pestana_registro, pestana_catalogo, pestana_historial = st.tabs([
    "📝 Nueva Venta & Preview", 
    "🏷️ Mi Catálogo", 
    "📊 Historial en Google Sheets"
])

with pestana_registro:
    col_izq, col_der = st.columns([1.1, 0.9])
    
    with col_izq:
        st.subheader("1. Datos Generales")
        f1, f2 = st.columns(2)
        with f1:
            folio_auto = f"DOC-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            folio = st.text_input("Folio / ID", value=folio_auto)
            cliente = st.text_input("Nombre del Cliente", placeholder="Ej: María Gómez")
            telefono = st.text_input("Teléfono / WhatsApp", placeholder="Ej: 981 123 4567")
            direccion = st.text_area(lbl_lugar.replace(":", ""), placeholder="Ej: Mostrador o Calle Hidalgo #5")

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
        st.subheader("2. Conceptos o Productos")
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
                            db.guardar_registro_venta(u_activo["usuario"], cabecera_data, st.session_state.partidas_actuales)
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
            st.image(pil_image, caption="Comprobante en tiempo real", use_container_width=True)
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

with pestana_catalogo:
    st.subheader("Catálogo de Productos y Servicios")
    with st.form("form_cat"):
        p_nom = st.text_input("Nombre del Concepto")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_costo = st.number_input("Costo Base ($)", min_value=0.0, step=10.0)
        with c2:
            p_margen = st.number_input("Margen (%)", min_value=0.0, value=35.0)
        with c3:
            p_precio = st.number_input("Precio al Público ($)", value=float(p_costo * (1 + p_margen/100)))
        
        if st.form_submit_button("Guardar en Google Sheets"):
            if p_nom.strip():
                with st.spinner("Guardando..."):
                    db.guardar_producto(u_activo["usuario"], {
                        "nombre": p_nom.strip(),
                        "costo_base": p_costo,
                        "margen_porcentaje": p_margen,
                        "precio_venta": p_precio
                    })
                st.success("Guardado en Google Sheets.")
            else:
                st.error("Ingresa el nombre del producto.")

with pestana_historial:
    st.subheader("Mis Ventas en Google Sheets")
    df_mis_ventas = db.obtener_ventas(u_activo["usuario"])
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

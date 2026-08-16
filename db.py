import requests
import json
import pandas as pd

APPSCRIPT_URL = "https://script.google.com/macros/s/AKfycbxjB5mqL0z8U6j-ySz8UO1Hn3KbEl1nifpwtB4zfC8_sfeRx--kcVetQozQ__dVKDIVwg/exec"

def request_cloud(payload: dict):
    try:
        response = requests.post(
            APPSCRIPT_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            allow_redirects=True,
            timeout=20
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- AUTENTICACIÓN, GOOGLE Y REGISTRO ---
def registrar_usuario(usuario_data: dict):
    return request_cloud({"tipo": "registro_usuario", "usuario_data": usuario_data})

def registrar_google(usuario_data: dict):
    return request_cloud({"tipo": "registro_google", "usuario_data": usuario_data})

def login_usuario(usuario: str, password: str):
    return request_cloud({"tipo": "login", "usuario": usuario, "password": password})

# --- EMPRENDIMIENTOS ---
def obtener_emprendimientos(usuario: str):
    res = request_cloud({"tipo": "obtener_emprendimientos", "usuario": usuario})
    if res.get("status") == "success" and res.get("data"):
        return res["data"]
    return []

def guardar_emprendimiento(usuario: str, emprendimiento: dict):
    return request_cloud({
        "tipo": "guardar_emprendimiento",
        "usuario": usuario,
        "emprendimiento": emprendimiento
    })

# --- CANAL DE SUGERENCIAS / FEEDBACK ---
def guardar_feedback(usuario: str, feedback: dict):
    return request_cloud({
        "tipo": "guardar_feedback",
        "usuario": usuario,
        "feedback": feedback
    })

# --- OPERACIONES COMERCIALES ---
def guardar_registro_venta(usuario_activo: str, cabecera: dict, partidas: list):
    return request_cloud({
        "tipo": "nueva_venta",
        "usuario_activo": usuario_activo,
        "cabecera": cabecera,
        "partidas": partidas
    })

def guardar_producto(usuario_activo: str, producto: dict):
    return request_cloud({
        "tipo": "nuevo_producto",
        "usuario_activo": usuario_activo,
        "producto": producto
    })

def obtener_ventas(usuario_activo: str, es_admin: bool = False):
    res = request_cloud({"tipo": "obtener_ventas", "usuario_activo": usuario_activo, "es_admin": es_admin})
    if res.get("status") == "success" and res.get("data"):
        return pd.DataFrame(res["data"])
    return pd.DataFrame()

def obtener_detalle_folio(folio: str):
    res = request_cloud({"tipo": "obtener_detalle", "folio": folio})
    if res.get("status") == "success" and res.get("data"):
        return pd.DataFrame(res["data"])
    return pd.DataFrame()

# --- MÓDULO ADMINISTRADOR ---
def admin_obtener_usuarios():
    res = request_cloud({"tipo": "admin_obtener_usuarios"})
    if res.get("status") == "success" and res.get("data"):
        return pd.DataFrame(res["data"])
    return pd.DataFrame()

def admin_actualizar_plan_suscripcion(usuario: str, nuevo_rol: str, nuevo_plan: str, dias_sumar: int, nuevo_estado: str):
    return request_cloud({
        "tipo": "admin_actualizar_plan_suscripcion",
        "usuario": usuario,
        "nuevo_rol": nuevo_rol,
        "nuevo_plan": nuevo_plan,
        "dias_sumar": dias_sumar,
        "nuevo_estado": nuevo_estado
    })

import sqlite3
import pandas as pd

DB_FILE = "ventas_entregas.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Tabla principal de ventas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            folio TEXT PRIMARY KEY,
            fecha_registro TEXT,
            cliente TEXT,
            telefono TEXT,
            direccion TEXT,
            fecha_entrega TEXT,
            horario_entrega TEXT,
            total REAL,
            anticipo REAL,
            saldo REAL,
            estado_pago TEXT,
            estado_entrega TEXT
        )
    """)
    
    # Detalle de productos por venta
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_venta TEXT,
            producto TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY (folio_venta) REFERENCES ventas (folio)
        )
    """)
    conn.commit()
    conn.close()

def guardar_registro_venta(cabecera: dict, partidas: list):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO ventas (
            folio, fecha_registro, cliente, telefono, direccion,
            fecha_entrega, horario_entrega, total, anticipo, saldo,
            estado_pago, estado_entrega
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cabecera["folio"],
        cabecera["fecha_registro"],
        cabecera["cliente"],
        cabecera["telefono"],
        cabecera["direccion"],
        cabecera["fecha_entrega"],
        cabecera["horario_entrega"],
        cabecera["total"],
        cabecera["anticipo"],
        cabecera["saldo"],
        cabecera["estado_pago"],
        cabecera["estado_entrega"]
    ))
    
    for item in partidas:
        cur.execute("""
            INSERT INTO ventas_detalle (folio_venta, producto, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cabecera["folio"],
            item["producto"],
            item["cantidad"],
            item["precio_unitario"],
            item["subtotal"]
        ))
        
    conn.commit()
    conn.close()

def obtener_ventas():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM ventas ORDER BY fecha_registro DESC", conn)
    conn.close()
    return df

def obtener_detalle_folio(folio: str):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT producto, cantidad, precio_unitario, subtotal FROM ventas_detalle WHERE folio_venta = ?", conn, params=(folio,))
    conn.close()
    return df

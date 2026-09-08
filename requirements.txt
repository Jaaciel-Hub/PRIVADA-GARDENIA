import streamlit as st
import json
import os
import base64
from datetime import datetime
import pandas as pd
from fpdf import FPDF

DB_FILE = "db.json"

USUARIOS = {
    "admin": {"password": "admin123", "rol": "admin"},
    "tesorero": {"password": "teso2026", "rol": "admin"},
    "vecino": {"password": "gardenia2026", "rol": "vecino"}
}

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"cuotas": [], "avisos": []}

def save(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

def fmt_anio(a):
    try:
        return str(int(float(a)))
    except:
        return str(a)

def crear_pdf(depto, mes, anio, monto, concepto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Privada Gardenia - Recibo", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, "Departamento: " + str(depto), ln=True)
    pdf.cell(0, 10, "Concepto: " + str(concepto), ln=True)
    pdf.cell(0, 10, "Periodo: " + str(mes) + " " + fmt_anio(anio), ln=True)
    pdf.cell(0, 10, "Monto: $" + str(monto), ln=True)
    pdf.cell(0, 10, "Fecha: " + datetime.now().strftime("%Y-%m-%d"), ln=True)
    pdf.ln(20)
    pdf.cell(0, 10, "Firma Tesorero", align="C")
    d = pdf.output(dest="S")
    if isinstance(d, str):
        return d.encode("latin-1")
    return bytes(d)

db = load()

st.title("Privada Gardenia")

if "ok" not in st.session_state:
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["password"] == p:
            st.session_state["ok"] = True
            st.session_state["usuario"] = u
            st.session_state["rol"] = USUARIOS[u]["rol"]
            st.rerun()
        else:
            st.error("Datos incorrectos")
    st.stop()

st.sidebar.write("Hola " + str(st.session_state.get("usuario")))
if st.sidebar.button("Salir"):
    st.session_state.clear()
    st.rerun()

es_admin = st.session_state.get("rol") == "admin"

tab1, tab2 = st.tabs(["Cuotas", "Avisos"])

with tab1:
    st.subheader("Cuotas")
    if es_admin:
        with st.expander("Registrar cuota"):
            with st.form("nc"):
                depto = st.text_input("Depto")
                monto = st.number_input("Monto", min_value=0.0)
                mes = st

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from datetime import date

st.set_page_config(page_title="Privada Gardenia", page_icon="🏡")
st.title("🏡 Privada Gardenia")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u=="admin" and p=="admin123":
            st.session_state.auth=True
            st.rerun()
        else:
            st.error("Datos incorrectos")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

def leer(ws):
    try:
        df = conn.read(worksheet=ws, ttl=0)
        return df.dropna(how="all") if df is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

def guardar(ws, df):
    conn.update(worksheet=ws, data=df)

menu = st.sidebar.selectbox("Menú", ["Vecinos", "Pagos", "Reporte"])

if menu=="

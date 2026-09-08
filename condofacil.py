import streamlit as st
import json, os
from datetime import date

DB_FILE = "data.json"
USUARIOS = {"admin": "admin123"}

def load():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE) as f: return json.load(f)
        except: pass
    return {"pagos": [], "avisos": ["Bienvenidos a Privada Gardenia"]}

def save(d):
    with open(DB_FILE, "w") as f: json.dump(d, f)

db = load()
st.title("Privada Gardenia")

if "ok" not in st.session_state:
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if USUARIOS.get(u) == p:
            st.session_state.ok = True
            st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

st.sidebar.write("Hola admin")
if st.sidebar.button("Salir"):
    st.session_state.clear(); st.rerun()

tab1, tab2 = st.tabs(["Cuotas", "Avisos"])
with tab1:
    st.subheader("Registrar pago")
    casa = st.text_input("Casa #")
    monto = st.number_input("Monto", 0)
    if st.button("Guardar pago"):
        db["pagos"].append({"casa":casa,"monto":monto,"fecha":str(date.today())})
        save(db); st.success("Guardado"); st.rerun()
    st.subheader("Historial")
    for pg in reversed(db["pagos"][-20:]):
        st.write(f"Casa {pg['casa']} - ${pg['monto']} - {pg['fecha']}")
with tab2:
    for a in db["avisos"]: st.info(a)
    nuevo = st.text_area("Nuevo aviso")
    if st.button("Publicar"):
        if nuevo:
            db["avisos"].append(nuevo); save(db); st.rerun()

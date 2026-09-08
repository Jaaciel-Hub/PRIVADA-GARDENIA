import streamlit as st
import json, os
from datetime import datetime

DB_FILE = "db.json"
USUARIOS = {"admin": {"password": "admin123", "rol": "admin"}, "tesorero": {"password": "teso2026", "rol": "admin"}, "vecino": {"password": "gardenia2026", "rol": "vecino"}}

def load():
    if not os.path.exists(DB_FILE):
        return {"cuotas": [], "avisos": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db = load()
st.title("Privada Gardenia")

if "ok" not in st.session_state:
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["password"] == p:
            st.session_state.ok = True
            st.session_state.usuario = u
            st.session_state.rol = USUARIOS[u]["rol"]
            st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

st.sidebar.write(f"Hola {st.session_state.usuario}")
if st.sidebar.button("Salir"):
    st.session_state.clear(); st.rerun()

es_admin = st.session_state.get("rol") == "admin"

tab1, tab2 = st.tabs(["Cuotas", "Avisos"])

with tab1:
    st.subheader("Cuotas por Departamento")
    if es_admin:
        with st.form("nueva_cuota"):
            depto = st.text_input("Número de departamento")
            monto = st.number_input("Monto", min_value=0.0)
            concepto = st.text_input("Concepto", value="Mantenimiento")
            if st.form_submit_button("Registrar"):
                db["cuotas"].append({"departamento": depto, "monto": monto, "concepto": concepto, "fecha": datetime.now().strftime("%Y-%m-%d"), "pagado": False})
                save(db); st.success("Registrado"); st.rerun()
    for i, c in enumerate(db.get("cuotas", [])):
        col1, col2 = st.columns([3,1])
        col1.write(f"Depto {c.get('departamento')} - ${c.get('monto')} - {c.get('concepto')} - {'Pagado' if c.get('pagado') else 'Pendiente'}")
        if es_admin:
            if col2.button("Pagado" if not c.get('pagado') else "Pendiente", key=f"c{i}"):
                db["cuotas"][i]["pagado"] = not db["cuotas"][i].get("pagado")
                save(db); st.rerun()

with tab2:
    st.subheader("Avisos")
    if es_admin:
        with st.form("nuevo_aviso"):
            titulo = st.text_input("Título")
            msg = st.text_area("Mensaje")
            if st.form_submit_button("Publicar"):
                db["avisos"].append({"titulo": titulo, "mensaje": msg, "fecha": datetime.now().strftime("%Y-%m-%d")})
                save(db); st.success("Publicado"); st.rerun()
    for a in reversed(db.get("avisos", [])):
        st.info(f"**{a.get('titulo')}** ({a.get('fecha')})\n\n{a.get('mensaje')}")

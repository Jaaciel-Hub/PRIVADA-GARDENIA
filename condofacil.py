import streamlit as st
import json, os

DB_FILE = "data.json"

def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f: return json.load(f)
    return {"usuarios": {"Vecino1":"1234"}, "avisos": []}

def save(d):
    with open(DB_FILE, "w") as f: json.dump(d, f)

db = load()
st.title("Privada Gardenia")

u = st.text_input("Usuario")
p = st.text_input("Clave", type="password")

if st.button("Entrar"):
    if db["usuarios"].get(u) == p:
        st.session_state.ok = True
        st.session_state.u = u
    else: st.error("Datos incorrectos")

if st.session_state.get("ok"):
    st.success(f"Hola {st.session_state.u}")
    st.subheader("Avisos")
    for a in db["avisos"]:
        st.info(a)
    nuevo = st.text_area("Nuevo aviso")
    if st.button("Publicar"):
        db["avisos"].append(nuevo)
        save(db)
        st.rerun()

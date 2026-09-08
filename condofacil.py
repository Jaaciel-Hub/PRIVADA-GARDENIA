import streamlit as st
import json, os
from datetime import datetime
import pandas as pd

DB_FILE = "db.json"
USUARIOS = {"admin": {"password": "admin123", "rol": "admin"}, "tesorero": {"password": "teso2026", "rol": "admin"}, "vecino": {"password": "gardenia2026", "rol": "vecino"}}
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

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
    u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["password"] == p:
            st.session_state.ok=True; st.session_state.usuario=u; st.session_state.rol=USUARIOS[u]["rol"]; st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

st.sidebar.write(f"Hola {st.session_state.usuario}")
if st.sidebar.button("Salir"):
    st.session_state.clear(); st.rerun()
es_admin = st.session_state.get("rol")=="admin"

tab1, tab2 = st.tabs(["Cuotas","Avisos"])
with tab1:
    st.subheader("Cuotas por Departamento")
    if es_admin:
        with st.expander("Registrar cuota"):
            with st.form("nc"):
                depto=st.text_input("Departamento"); monto=st.number_input("Monto",min_value=0.0)
                mes=st.selectbox("Mes",MESES); anio=st.number_input("Año",value=2026,step=1)
                concepto=st.text_input("Concepto",value="Mantenimiento")
                if st.form_submit_button("Guardar"):
                    db["cuotas"].append({"departamento":depto,"monto":monto,"mes":mes,"anio":int(anio),"concepto":concepto,"pagado":False,"fecha":datetime.now().strftime("%Y-%m-%d")})
                    save(db); st.success("Guardado"); st.rerun()
    cuotas=db.get("cuotas",[])
    if cuotas:
        df=pd.DataFrame(cuotas)
        # Resumen adeudos
        st.write("### Adeudos por departamento")
        pendientes=df[df["pagado"]==False] if "pagado" in df else df
        if not pendientes.empty:
            resumen=pendientes.groupby("departamento")["monto"].sum().reset_index()
            st.dataframe(resumen,use_container_width=True)
        else:
            st.success("Sin adeudos 🎉")
        st.write("### Detalle")
        filtro=st.selectbox("Filtrar mes",["Todos"]+MESES)
        dff=df if filtro=="Todos" else df[df["mes"]==filtro]
        for i,row in dff.iterrows():
            c1,c2=st.columns([3,1])
            c1.write(f"Depto {row['departamento']} | {row['mes']} {row['anio']} | ${row['monto']} | {'✅' if row['pagado'] else '❌'}")
            if es_admin and c2.button("Cambiar",key=f"b{i}"):
                # buscar indice real
                idx=cuotas.index(row.to_dict()) if row.to_dict() in cuotas else i
                db["cuotas"][idx]["pagado"]=not db["cuotas"][idx]["pagado"]; save(db); st.rerun()
    else:
        st.info("No hay cuotas registradas")

with tab2:
    st.subheader("Avisos")
    if es_admin:
        with st.form("na"):
            t=st.text_input("Título"); m=st.text_area("Mensaje")
            if st.form_submit_button("Publicar"):
                db["avisos"].append({"titulo":t,"mensaje":m,"fecha":datetime.now().strftime("%Y-%m-%d")}); save(db); st.rerun()
    for a in reversed(db.get("avisos",[])):
        st.info(f"**{a.get('titulo')}** ({a.get('fecha')})\n\n{a.get('mensaje')}")

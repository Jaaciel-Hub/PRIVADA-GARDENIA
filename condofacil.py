import streamlit as st
import json, os, base64
from datetime import datetime
import pandas as pd
from fpdf import FPDF

DB_FILE="db.json"
USUARIOS={"admin":{"password":"admin123","rol":"admin"},"tesorero":{"password":"teso2026","rol":"admin"},"vecino":{"password":"gardenia2026","rol":"vecino"}}
MESES=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def load():
    return json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else {"cuotas":[],"avisos":[]}
def save(db): json.dump(db, open(DB_FILE,"w"))

def fmt_anio(a):
    try: return str(int(float(a)))
    except: return str(a)

def crear_pdf(depto,mes,anio,monto,concepto):
    pdf=FPDF(); pdf.add_page()
    pdf.set_font("Arial","B",16); pdf.cell(0,10,"Privada Gardenia - Recibo",ln=True,align="C")
    pdf.set_font("Arial","",12); pdf.ln(10)
    pdf.cell(0,10,f"Departamento: {depto}",ln=True)
    pdf.cell(0,10,f"Concepto: {concepto}",ln=True)
    pdf.cell(0,10,f"Periodo: {mes} {fmt_anio(anio)}",ln=True)
    pdf.cell(0,10,f"Monto: ${monto}",ln=True)
    pdf.cell(0,10,f"Fecha: {datetime.now().strftime('%Y-%m-%d')}",ln=True)
    pdf.ln(20); pdf.cell(0,10,"_________________________ Firma Tesorero",align="C")
    d=pdf.output(dest="S")
    return d.encode("latin-1") if isinstance(d,str) else bytes(d)

db=load()
st.title("Privada Gardenia")
if "ok" not in st.session_state:
    u=st.text_input("Usuario"); p=st.text_input("Clave",type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["password"]==p:
            st.session_state.ok=True; st.session_state.usuario=u; st.session_state.rol=USUARIOS[u]["rol"]; st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

st.sidebar.write(f"Hola {st.session_state.usuario}")
if st.sidebar.button("Salir"): st.session_state.clear(); st.rerun()
es_admin=st.session_state.get("rol")=="admin"

tab1,tab2=st.tabs(["Cuotas","Avisos"])
with tab1:
    st.subheader("Cuotas")
    if es_admin:
        with st.expander("Registrar cuota"):
            with st.form("nc"):
                depto=st.text_input("Depto"); monto=st.number_input("Monto",min_value=0.0)
                mes=st.selectbox("Mes",MESES); anio=st.number_input("Año",value=2026,step=1)
                concepto=st.text_input("Concepto",value="Mantenimiento")
                if st.form_submit_button("Guardar"):
                    db["cuotas"].append({"departamento":depto,"monto":monto,"mes":mes,"anio":int(anio),"concepto":concepto,"pagado":False}); save(db); st.rerun()
    cuotas=db.get("cuotas",[])
    if cuotas:
        df=pd.DataFrame(cuotas)
        pendientes=df[df["pagado"]==False] if "pagado" in df else df
        st.write("### Adeudos por depto")
        if not pendientes.empty:
            st.dataframe(pendientes.groupby("departamento")["monto"].sum().reset_index(),use_container_width=True)
        else: st.success("Sin adeudos")
        for i,row in df.iterrows():
            c1,c2,c3=st.columns([3,1,1])
            c1.write(f"{row['departamento']} | {row['mes']} {fmt_anio(row['anio'])} | ${row['monto']} {'✅' if row['pagado'] else '❌'}")
            if es_admin:
                if c2.button("✓/✗",key=f"t{i}"):
                    db["cuotas"][i]["pagado"]=not db["cuotas"][i]["pagado"]; save(db); st.rerun()
                pdf_bytes=crear_pdf(row['departamento'],row['mes'],row['anio'],row['monto'],row['concepto'])
                c3.download_button("PDF",pdf_bytes,f"recibo_{row['departamento']}_{row['mes']}.pdf","application/pdf",key=f"p{i}")
    else: st.info("No hay cuotas")

with

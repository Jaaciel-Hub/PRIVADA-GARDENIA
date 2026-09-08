import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection
import base64

USUARIOS = {
    "admin": {"password": "admin123", "rol": "admin"},
    "tesorero": {"password": "teso2026", "rol": "admin"},
    "vecino": {"password": "gardenia2026", "rol": "vecino"}
}
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def fmt_anio(a):
    try: return str(int(float(a)))
    except: return str(a)

def crear_pdf(depto, mes, anio, monto, concepto):
    pdf = FPDF(); pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Privada Gardenia - Recibo", ln=True, align="C")
    pdf.set_font("Arial", "", 12); pdf.ln(10)
    pdf.cell(0, 10, "Departamento: " + str(depto), ln=True)
    pdf.cell(0, 10, "Concepto: " + str(concepto), ln=True)
    pdf.cell(0, 10, "Periodo: " + str(mes) + " " + fmt_anio(anio), ln=True)
    pdf.cell(0, 10, "Monto: $" + str(monto), ln=True)
    pdf.cell(0, 10, "Fecha: " + datetime.now().strftime("%Y-%m-%d"), ln=True)
    pdf.ln(20); pdf.cell(0, 10, "Firma Tesorero", align="C")
    d = pdf.output(dest="S")
    return d.encode("latin-1") if isinstance(d, str) else bytes(d)

st.set_page_config(page_title="Privada Gardenia", page_icon="🏡")
st.title("🏡 Privada Gardenia")

if "ok" not in st.session_state:
    u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["password"] == p:
            st.session_state["ok"]=True; st.session_state["usuario"]=u; st.session_state["rol"]=USUARIOS[u]["rol"]; st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

st.sidebar.write("Hola " + st.session_state["usuario"])
if st.sidebar.button("Salir"): st.session_state.clear(); st.rerun()
es_admin = st.session_state["rol"] == "admin"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_cuotas():
    try:
        df = conn.read(worksheet="cuotas", ttl=0)
        return df.fillna("") if df is not None else pd.DataFrame(columns=["departamento","monto","mes","anio","concepto","pagado"])
    except: return pd.DataFrame(columns=["departamento","monto","mes","anio","concepto","pagado"])

def load_avisos():
    try:
        df = conn.read(worksheet="avisos", ttl=0)
        return df.fillna("") if df is not None else pd.DataFrame(columns=["titulo","mensaje","fecha","foto"])
    except: return pd.DataFrame(columns=["titulo","mensaje","fecha","foto"])

tab1, tab2 = st.tabs(["Cuotas", "Avisos"])

with tab1:
    st.subheader("Cuotas")
    df = load_cuotas()
    if es_admin:
        with st.expander("Registrar cuota"):
            with st.form("nc", clear_on_submit=True):
                depto=st.text_input("Depto"); monto=st.number_input("Monto",min_value=0.0)
                mes=st.selectbox("Mes",MESES); anio=st.number_input("Año",value=2026,step=1)
                concepto=st.text_input("Concepto",value="Mantenimiento")
                if st.form_submit_button("Guardar"):
                    nueva=pd.DataFrame([{"departamento":depto,"monto":monto,"mes":mes,"anio":int(anio),"concepto":concepto,"pagado":False}])
                    conn.update(worksheet="cuotas", data=pd.concat([df,nueva],ignore_index=True)); st.rerun()
    if not df.empty:
        df["pagado_bool"]=df["pagado"].astype(str).str.lower().isin(["true","1","si","yes"])
        pendientes=df[~df["pagado_bool"]].copy()
        st.write("Adeudos por depto")
        if not pendientes.empty:
            pendientes["monto"]=pd.to_numeric(pendientes["monto"],errors="coerce").fillna(0)
            st.dataframe(pendientes.groupby("departamento")["monto"].sum().reset_index(),use_container_width=True)
        else: st.success("Sin adeudos")
        for i,row in df.iterrows():
            c1,c2,c3=st.columns([3,1,1])
            estado="✅" if row["pagado_bool"] else "❌"
            c1.write(f"{row['departamento']} | {row['mes']} {fmt_anio(row['anio'])} | ${row['monto']} {estado}")
            if es_admin:
                if c2.button("✓/✗",key=f"t{i}"):
                    df.at[i,"pagado"]=not row["pagado_bool"]
                    conn.update(worksheet="cuotas", data=df.drop(columns=["pagado_bool"])); st.rerun()
                pdf_bytes=crear_pdf(row["departamento"],row["mes"],row["anio"],row["monto"],row["concepto"])
                c3.download_button("PDF",pdf_bytes,f"recibo_{row['departamento']}_{row['mes']}.pdf","application/pdf",key=f"p{i}")
    else: st.info("No hay cuotas")

with tab2:
    st.subheader("Muro de Avisos")
    df_a=load_avisos()
    if es_admin:
        with st.expander("Nuevo aviso con foto"):
            with st.form("na", clear_on_submit=True):
                t=st.text_input("Título"); m=st.text_area("Mensaje")
                foto=st.file_uploader("Foto (opcional)",type=["png","jpg","jpeg"])
                if st.form_submit_button("Publicar"):
                    foto_b64=base64.b64encode(foto.read()).decode() if foto else ""
                    nueva=pd.DataFrame([{"titulo":t,"mensaje":m,"fecha":datetime.now().strftime("%Y-%m-%d"),"foto":foto_b64}])
                    conn.update(worksheet="avisos", data=pd.concat([df_a,nueva],ignore_index=True)); st.rerun()
    if not df_a.empty:
        for idx in reversed(range(len(df_a))):
            a=df_a.iloc[idx]
            st.markdown("### "+str(a.get("titulo","")))
            st.caption(str(a.get("fecha","")))
            st.write(str(a.get("mensaje","")))
            if str(a.get("foto",""))!="":
                try: st.image(base64.b64decode(str(a.get("foto"))),use_container_width=True)
                except: pass
            st.divider()
    else: st.info("No hay avisos")

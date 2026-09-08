import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date

st.set_page_config(page_title="Privada Gardenia")
st.title("Privada Gardenia - Prueba")

if "auth" not in st.session_state:
    st.session_state.auth = False
if "vecinos" not in st.session_state:
    st.session_state.vecinos = pd.DataFrame(columns=["casa","nombre","telefono"])
if "pagos" not in st.session_state:
    st.session_state.pagos = pd.DataFrame(columns=["fecha","casa","monto","concepto","pagado"])

if not st.session_state.auth:
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("admin / admin123")
    st.stop()

opcion = st.sidebar.selectbox("Menu", ["Vecinos", "Pagos", "Reporte"])

if opcion == "Vecinos":
    st.header("Vecinos")
    with st.form("nv", clear_on_submit=True):
        casa = st.text_input("Casa")
        nombre = st.text_input("Nombre")
        tel = st.text_input("Telefono")
        if st.form_submit_button("Guardar"):
            df = st.session_state.vecinos
            nuevo = pd.DataFrame([{"casa":casa,"nombre":nombre,"telefono":tel}])
            st.session_state.vecinos = pd.concat([df,nuevo], ignore_index=True)
            st.success("Guardado")
            st.rerun()
    st.dataframe(st.session_state.vecinos, use_container_width=True)

if opcion == "Pagos":
    st.header("Pagos")
    dfv = st.session_state.vecinos
    casas = dfv["casa"].tolist() if not dfv.empty else []
    with st.form("np", clear_on_submit=True):
        casa = st.selectbox("Casa", casas) if casas else st.text_input("Casa")
        monto = st.number_input("Monto", min_value=0.0)
        concepto = st.text_input("Concepto", value="Mantenimiento")
        pagado = st.checkbox("Pagado", value=True)
        if st.form_submit_button("Guardar pago"):
            df = st.session_state.pagos
            nuevo = pd.DataFrame([{"fecha":str(date.today()),"casa":casa,"monto":monto,"concepto":concepto,"pagado":"SI" if pagado else "NO"}])
            st.session_state.pagos = pd.concat([df,nuevo], ignore_index=True)
            st.success("Guardado")
            st.rerun()
    st.dataframe(st.session_state.pagos, use_container_width=True)

if opcion == "Reporte":
    st.header("Adeudos")
    df = st.session_state.pagos
    if not df.empty:
        pend = df[df["pagado"]=="NO"]
        st.metric("Total pendiente", f"${pend['monto'].sum():,.2f}" if not pend.empty else "$0")
        st.dataframe(pend, use_container_width=True)
        if st.button("Generar PDF") and not pend.empty:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial","B",16)
            pdf.cell(0,10,"Privada Gardenia - Adeudos",ln=True,align="C")
            pdf.set_font("Arial","",10)
            for _,r in pend.iterrows():
                pdf.cell(0,8,f"{r['fecha']} - Casa {r['casa']} - ${r['monto']}",ln=True)
            pdf.output("/tmp/reporte.pdf")
            with open("/tmp/reporte.pdf","rb") as f:
                st.download_button("Descargar", f, "adeudos.pdf")
    else:
        st.info("Sin pagos")

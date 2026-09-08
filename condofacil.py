import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from datetime import date

st.set_page_config(page_title="Privada Gardenia", page_icon="house")
st.title("Privada Gardenia")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Datos incorrectos")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

def leer(ws):
    try:
        df = conn.read(worksheet=ws, ttl=0)
        return df.dropna(how="all") if df is not None else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def guardar(ws, df):
    conn.update(worksheet=ws, data=df)

opcion = st.sidebar.selectbox("Menu", ["Vecinos", "Pagos", "Reporte"])

if opcion == "Vecinos":
    st.header("Vecinos")
    df = leer("vecinos")
    with st.form("nv", clear_on_submit=True):
        casa = st.text_input("Casa / Lote")
        nombre = st.text_input("Nombre")
        tel = st.text_input("Telefono")
        if st.form_submit_button("Guardar"):
            nueva = pd.DataFrame([{"casa": casa, "nombre": nombre, "telefono": tel}])
            df = pd.concat([df, nueva], ignore_index=True)
            guardar("vecinos", df)
            st.success("Guardado")
            st.rerun()
    if not df.empty:
        st.dataframe(df, use_container_width=True)

if opcion == "Pagos":
    st.header("Registrar pago")
    df = leer("pagos")
    vecinos = leer("vecinos")
    casas = vecinos["casa"].tolist() if not vecinos.empty and "casa" in vecinos.columns else []
    with st.form("np", clear_on_submit=True):
        if casas:
            casa = st.selectbox("Casa", casas)
        else:
            casa = st.text_input("Casa")
        monto = st.number_input("Monto", min_value=0.0)
        concepto = st.text_input("Concepto", value="Mantenimiento")
        pagado = st.checkbox("Pagado", value=True)
        if st.form_submit_button("Guardar pago"):
            nueva = pd.DataFrame([{"fecha": str(date.today()), "casa": casa, "monto": monto, "concepto": concepto, "pagado": "SI" if pagado else "NO"}])
            df = pd.concat([df, nueva], ignore_index=True)
            guardar("pagos", df)
            st.success("Pago guardado")
            st.rerun()
    if not df.empty:
        st.dataframe(df, use_container_width=True)

if opcion == "Reporte":
    st.header("Reporte de adeudos")
    df = leer("pagos")
    if not df.empty:
        pendientes = df[df["pagado"] == "NO"]
        total = pendientes["monto"].sum() if not pendientes.empty else 0
        st.metric("Total pendiente", f"${total:,.2f}")
        st.dataframe(pendientes, use_container_width=True)
        if st.button("Generar PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Privada Gardenia - Adeudos", ln=True, align="C")
            pdf.set_font("Arial", "", 10)
            for _, r in pendientes.iterrows():
                pdf.cell(0, 8, f"{r['fecha']} - Casa {r['casa']} - ${r['monto']} - {r['concepto']}", ln=True)
            pdf.output("/tmp/reporte.pdf")
            with open("/tmp/reporte.pdf", "rb") as f:
                st.download_button("Descargar PDF", f, "adeudos.pdf")
    else:
        st.info("Sin pagos registrados")

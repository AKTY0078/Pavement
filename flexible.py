import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="AASHTO Pavement Design", layout="centered")

# ==============================
# ฟังก์ชัน
# ==============================
def get_Zr(reliability):
    table = {
        50: 0.0,
        75: -0.674,
        85: -1.036,
        90: -1.282,
        95: -1.645,
        99: -2.327
    }
    return table.get(reliability, -1.645)

def calculate_SN(W18, Zr, So, delta_PSI, Mr):
    SN = 3.0  
    for i in range(1000):
        logW18 = (
            Zr * So +
            9.36 * math.log10(SN + 1) -
            0.20 +
            math.log10(delta_PSI / (4.2 - 1.5)) /
            (0.4 + (1094 / (SN + 1)**5.19)) +
            2.32 * math.log10(Mr) -
            8.07
        )

        W18_calc = 10 ** logW18
        error = W18 - W18_calc
        SN += error / 1e7

        if abs(error) < 1000:
            break

    return SN

def calculate_layers(SN, a1, a2, a3, m2, m3):
    D1 = SN * 0.4 / a1
    D2 = SN * 0.3 / (a2 * m2)
    D3 = SN * 0.3 / (a3 * m3)
    return D1, D2, D3

def inch_to_cm(x):
    return x * 2.54

# ==============================
# UI
# ==============================
st.title("🚧 AASHTO 1993 Pavement Design Tool")
st.markdown("### Flexible Pavement (งานออกแบบถนนลาดยาง)")

# INPUT
st.subheader("📥 Input Parameters")

W18 = st.number_input("Traffic (W18 - ESAL)", value=1e7, format="%.0f")

reliability = st.selectbox("Reliability (%)", [50, 75, 85, 90, 95, 99], index=4)
Zr = get_Zr(reliability)

So = st.number_input("Standard Deviation (So)", value=0.45)
delta_PSI = st.number_input("ΔPSI", value=1.7)
Mr = st.number_input("Subgrade Modulus (psi)", value=8000.0)

st.markdown("### Layer Coefficients")
a1 = st.number_input("a1 (Asphalt)", value=0.44)
a2 = st.number_input("a2 (Base)", value=0.14)
a3 = st.number_input("a3 (Subbase)", value=0.11)

m2 = st.number_input("m2 (Drainage Base)", value=1.0)
m3 = st.number_input("m3 (Drainage Subbase)", value=1.0)

# ==============================
# CALCULATE
# ==============================
if st.button("🚀 Calculate"):
    SN = calculate_SN(W18, Zr, So, delta_PSI, Mr)
    D1, D2, D3 = calculate_layers(SN, a1, a2, a3, m2, m3)

    # แปลงหน่วย
    D1_cm, D2_cm, D3_cm = inch_to_cm(D1), inch_to_cm(D2), inch_to_cm(D3)

    st.success("✅ Calculation Complete")

    # แสดงผล
    st.subheader("📊 Results")
    st.metric("Structural Number (SN)", f"{SN:.2f}")

    st.write("### Thickness")
    st.write(f"AC: {D1:.2f} in ({D1_cm:.1f} cm)")
    st.write(f"Base: {D2:.2f} in ({D2_cm:.1f} cm)")
    st.write(f"Subbase: {D3:.2f} in ({D3_cm:.1f} cm)")

    # Minimum check
    st.subheader("⚠️ Minimum Thickness Check")
    if D1_cm < 5:
        st.warning("AC บางเกินไป (< 5 cm)")
    if D2_cm < 10:
        st.warning("Base บางเกินไป (< 10 cm)")
    if D3_cm < 10:
        st.warning("Subbase บางเกินไป (< 10 cm)")

    # Export
    df = pd.DataFrame({
        "Layer": ["AC", "Base", "Subbase"],
        "Thickness (in)": [D1, D2, D3],
        "Thickness (cm)": [D1_cm, D2_cm, D3_cm]
    })

    st.download_button(
        "📥 Download Results (CSV)",
        df.to_csv(index=False),
        file_name="pavement_design.csv",
        mime="text/csv"
    )

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("Developed for Civil Engineering - AASHTO 1993 Design")

import math
import streamlit as st
import pandas as pd

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Pavement Design", layout="wide")

# ======================
# FUNCTIONS
# ======================
def get_Zr(r):
    return {
        50: 0.0, 75: -0.674, 85: -1.036,
        90: -1.282, 95: -1.645, 99: -2.327
    }[r]

# -------- Flexible --------
def calculate_SN(W18, Zr, So, dPSI, Mr):
    SN = 3.0
    for _ in range(1000):
        logW18 = (
            Zr * So +
            9.36 * math.log10(SN + 1) -
            0.20 +
            math.log10(dPSI / (4.2 - 1.5)) /
            (0.4 + (1094 / (SN + 1)**5.19)) +
            2.32 * math.log10(Mr) -
            8.07
        )
        W_calc = 10 ** logW18
        SN += (W18 - W_calc) / 1e7
    return SN

def layers(SN, a1, a2, a3, m2, m3):
    return (
        SN * 0.4 / a1,
        SN * 0.3 / (a2*m2),
        SN * 0.3 / (a3*m3)
    )

# -------- Rigid (FIXED) --------
def calculate_rigid_AASHTO(W18, Zr, So, Sc, k, dPSI, J, Cd):
    D = 8.0

    for _ in range(1000):
        # 🔒 กันค่าพัง
        if D < 1:
            D = 1.0

        psi_ratio = max(dPSI / (4.5 - 1.5), 0.01)

        try:
            term1 = Zr * So
            term2 = 7.35 * math.log10(D + 1) - 0.06
            term3 = math.log10(psi_ratio)
            term4 = 1 / (1 + (1.624e7 / (D + 1)**8.46))
            term5 = (4.22 - 0.32 * J) * math.log10(max(Sc, 1))
            term6 = 0.75 * math.log10(max(k, 1))
            term7 = -8.0

            logW18 = term1 + term2 + (term3 * term4) + term5 + term6 + term7
            W_calc = 10 ** logW18

            error = W18 - W_calc

            # 🔒 ลด step กันแกว่ง
            D += error / 5e7

        except:
            D = 8.0

    return D

def inch_to_cm(x):
    return x * 2.54

# ======================
# DRAW
# ======================
def draw_flexible(D1, D2, D3):
    total = D1 + D2 + D3
    def h(d): return int((d/total)*300)

    return f"""
    <div style="width:200px;margin:auto;">
        <div style="background:#2E86C1;height:{h(D1)}px;color:white;text-align:center;">
            AC<br>{D1:.1f} in
        </div>
        <div style="background:#27AE60;height:{h(D2)}px;color:white;text-align:center;">
            Base<br>{D2:.1f} in
        </div>
        <div style="background:#A04000;height:{h(D3)}px;color:white;text-align:center;">
            Subbase<br>{D3:.1f} in
        </div>
    </div>
    """

def draw_rigid(D):
    return f"""
    <div style="width:200px;margin:auto;">
        <div style="background:#BDC3C7;height:220px;text-align:center;padding-top:90px;">
            Concrete<br>{D:.1f} in
        </div>
        <div style="background:#7F8C8D;height:60px;color:white;text-align:center;">
            Subgrade
        </div>
    </div>
    """

# ======================
# SIDEBAR
# ======================
st.sidebar.title("⚙️ Input")

pavement_type = st.sidebar.selectbox(
    "Pavement Type",
    ["Flexible (Asphalt)", "Rigid (Concrete)"]
)

W18 = st.sidebar.number_input("Traffic (ESAL)", value=1e7)
rel = st.sidebar.selectbox("Reliability (%)", [50,75,85,90,95,99], index=4)
Zr = get_Zr(rel)

So = st.sidebar.number_input("So", value=0.45)

# -------- Flexible --------
if pavement_type == "Flexible (Asphalt)":
    dPSI = st.sidebar.number_input("ΔPSI", value=1.7)
    Mr = st.sidebar.number_input("Mr (psi)", value=8000.0)

    a1 = st.sidebar.number_input("a1", value=0.44)
    a2 = st.sidebar.number_input("a2", value=0.14)
    a3 = st.sidebar.number_input("a3", value=0.11)
    m2 = st.sidebar.number_input("m2", value=1.0)
    m3 = st.sidebar.number_input("m3", value=1.0)

# -------- Rigid --------
else:
    Sc = st.sidebar.number_input("Sc (psi)", value=650.0)
    k = st.sidebar.number_input("k (pci)", value=100.0)
    dPSI = st.sidebar.number_input("ΔPSI", value=1.5)
    J = st.sidebar.number_input("J", value=3.2)
    Cd = st.sidebar.number_input("Cd", value=1.0)

# ======================
# MAIN
# ======================
st.title("🚧 Pavement Design (AASHTO 1993)")

if st.button("🚀 Calculate"):

    # -------- Flexible --------
    if pavement_type == "Flexible (Asphalt)":
        SN = calculate_SN(W18, Zr, So, dPSI, Mr)
        D1, D2, D3 = layers(SN, a1, a2, a3, m2, m3)

        st.metric("SN", f"{SN:.2f}")
        st.metric("AC", f"{D1:.2f} in / {inch_to_cm(D1):.1f} cm")
        st.metric("Base", f"{D2:.2f} in / {inch_to_cm(D2):.1f} cm")
        st.metric("Subbase", f"{D3:.2f} in / {inch_to_cm(D3):.1f} cm")

        st.markdown(draw_flexible(D1, D2, D3), unsafe_allow_html=True)

    # -------- Rigid --------
    else:
        D = calculate_rigid_AASHTO(W18, Zr, So, Sc, k, dPSI, J, Cd)

        st.metric("Concrete Thickness", f"{D:.2f} in / {inch_to_cm(D):.1f} cm")

        st.markdown(draw_rigid(D), unsafe_allow_html=True)

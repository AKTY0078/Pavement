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

def inch_to_cm(x):
    return x * 2.54

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

# -------- Rigid (fixed) --------
def calculate_rigid_AASHTO(W18, Zr, So, Sc, k, dPSI, J, Cd):
    D = 8.0
    for _ in range(1000):
        if D < 1:
            D = 1.0

        psi_ratio = max(dPSI / (4.5 - 1.5), 0.01)

        term1 = Zr * So
        term2 = 7.35 * math.log10(D + 1) - 0.06
        term3 = math.log10(psi_ratio)
        term4 = 1 / (1 + (1.624e7 / (D + 1)**8.46))
        term5 = (4.22 - 0.32 * J) * math.log10(max(Sc, 1))
        term6 = 0.75 * math.log10(max(k, 1))
        term7 = -8.0

        logW18 = term1 + term2 + (term3 * term4) + term5 + term6 + term7
        W_calc = 10 ** logW18
        D += (W18 - W_calc) / 5e7

    return D

# ======================
# SCALE LOGIC 🔥
# ======================
def get_scale_step(total_cm):
    if total_cm <= 20:
        return 2
    elif total_cm <= 50:
        return 5
    else:
        return 10

# ======================
# DRAW FLEXIBLE
# ======================
def draw_flexible(D1, D2, D3):
    total = D1 + D2 + D3
    total_cm = inch_to_cm(total)
    step = get_scale_step(total_cm)

    def h(d): return int((d/total)*300)

    scale_marks = ""
    for i in range(0, int(total_cm)+step, step):
        pos = int((i / total_cm) * 300)
        scale_marks += f"""
        <div style="position:absolute; bottom:{pos}px; left:0; font-size:10px;">
            ─ {i} cm
        </div>
        """

    return f"""
    <div style="display:flex; justify-content:center;">

        <div style="position:relative; width:60px; height:300px; color:white;">
            {scale_marks}
        </div>

        <div style="width:200px;
                    border-radius:12px;
                    overflow:hidden;
                    box-shadow:0 4px 15px rgba(0,0,0,0.5);">

            <div style="background:linear-gradient(135deg,#1f4e79,#2e86c1);
                        height:{h(D1)}px;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        color:white;">
                AC<br>{D1:.1f} in
            </div>

            <div style="background:linear-gradient(135deg,#1e8449,#52be80);
                        height:{h(D2)}px;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        color:white;">
                Base<br>{D2:.1f} in
            </div>

            <div style="background:linear-gradient(135deg,#935116,#d68910);
                        height:{h(D3)}px;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        color:white;">
                Subbase<br>{D3:.1f} in
            </div>
        </div>
    </div>
    """

# ======================
# DRAW RIGID
# ======================
def draw_rigid(D):
    total_cm = inch_to_cm(D)
    step = get_scale_step(total_cm)

    scale_marks = ""
    for i in range(0, int(total_cm)+step, step):
        pos = int((i / total_cm) * 300)
        scale_marks += f"""
        <div style="position:absolute; bottom:{pos}px; left:0; font-size:10px;">
            ─ {i} cm
        </div>
        """

    return f"""
    <div style="display:flex; justify-content:center;">

        <div style="position:relative; width:60px; height:300px; color:white;">
            {scale_marks}
        </div>

        <div style="width:200px;
                    border-radius:12px;
                    overflow:hidden;
                    box-shadow:0 4px 15px rgba(0,0,0,0.5);">

            <div style="background:#BDC3C7;height:300px;
                        display:flex;
                        justify-content:center;
                        align-items:center;">
                Concrete<br>{D:.1f} in
            </div>
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

    if pavement_type == "Flexible (Asphalt)":
        SN = calculate_SN(W18, Zr, So, dPSI, Mr)
        D1, D2, D3 = layers(SN, a1, a2, a3, m2, m3)

        st.metric("SN", f"{SN:.2f}")
        st.markdown(draw_flexible(D1, D2, D3), unsafe_allow_html=True)

    else:
        D = calculate_rigid_AASHTO(W18, Zr, So, Sc, k, dPSI, J, Cd)

        st.metric("Concrete Thickness", f"{D:.2f} in")
        st.markdown(draw_rigid(D), unsafe_allow_html=True)

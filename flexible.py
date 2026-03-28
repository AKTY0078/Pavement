import math
import streamlit as st
import pandas as pd

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="Pavement Design", layout="wide")

# ======================
# STYLE
# ======================
st.markdown("""
<style>
.block {
    border-radius: 10px;
    padding: 10px;
    color: white;
    text-align: center;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ======================
# FUNCTIONS
# ======================
def get_Zr(r):
    return {
        50: 0.0, 75: -0.674, 85: -1.036,
        90: -1.282, 95: -1.645, 99: -2.327
    }[r]

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

def inch_to_cm(x):
    return x * 2.54

# ======================
# DRAW (NO LIBRARY)
# ======================
def draw_layers_html(D1, D2, D3):
    total = D1 + D2 + D3

    def h(d):  # scale ความสูง
        return int((d / total) * 300)

    html = f"""
    <div style="width:200px; margin:auto;">
        <div class="block" style="background:#2E86C1;height:{h(D1)}px;">
            AC<br>{D1:.1f} in
        </div>
        <div class="block" style="background:#27AE60;height:{h(D2)}px;">
            Base<br>{D2:.1f} in
        </div>
        <div class="block" style="background:#A04000;height:{h(D3)}px;">
            Subbase<br>{D3:.1f} in
        </div>
    </div>
    """
    return html

# ======================
# SIDEBAR
# ======================
st.sidebar.title("⚙️ Input")

W18 = st.sidebar.number_input("Traffic (ESAL)", value=1e7)
rel = st.sidebar.selectbox("Reliability (%)", [50,75,85,90,95,99], index=4)
Zr = get_Zr(rel)

So = st.sidebar.number_input("So", value=0.45)
dPSI = st.sidebar.number_input("ΔPSI", value=1.7)
Mr = st.sidebar.number_input("Mr (psi)", value=8000.0)

st.sidebar.markdown("---")
a1 = st.sidebar.number_input("a1", value=0.44)
a2 = st.sidebar.number_input("a2", value=0.14)
a3 = st.sidebar.number_input("a3", value=0.11)
m2 = st.sidebar.number_input("m2", value=1.0)
m3 = st.sidebar.number_input("m3", value=1.0)

# ======================
# MAIN
# ======================
st.title("🚧 Pavement Design (AASHTO 1993)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Input Summary")
    st.write(f"Traffic: {W18:,.0f}")
    st.write(f"Reliability: {rel}%")
    st.write(f"Mr: {Mr}")

with col2:
    if st.button("🚀 Calculate"):
        SN = calculate_SN(W18, Zr, So, dPSI, Mr)
        D1, D2, D3 = layers(SN, a1, a2, a3, m2, m3)

        st.subheader("📊 Results")
        st.metric("SN", f"{SN:.2f}")
        st.metric("AC", f"{D1:.2f} in / {inch_to_cm(D1):.1f} cm")
        st.metric("Base", f"{D2:.2f} in / {inch_to_cm(D2):.1f} cm")
        st.metric("Subbase", f"{D3:.2f} in / {inch_to_cm(D3):.1f} cm")

        st.subheader("🧱 Pavement Structure")
        st.markdown(draw_layers_html(D1, D2, D3), unsafe_allow_html=True)

        # Export
        df = pd.DataFrame({
            "Layer": ["AC","Base","Subbase"],
            "inch": [D1,D2,D3],
            "cm": [inch_to_cm(D1), inch_to_cm(D2), inch_to_cm(D3)]
        })

        st.download_button("📥 Download CSV", df.to_csv(index=False), "design.csv")

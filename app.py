import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Beam Analysis App", page_icon="🏗", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, rgba(240,248,255,0.9), rgba(224,242,241,0.9)),
                    url('https://cdn.pixabay.com/photo/2016/11/29/10/07/architecture-1867187_1280.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
        color: #1a1a1a;
    }
    .main-header {
        background: linear-gradient(90deg, #80DEEA, #B2EBF2);
        border-radius: 25px;
        text-align: center;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 3rem;
        color: #004D40;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .main-header h3 {
        color: #00796B;
        font-weight: 500;
    }
    .glass-panel {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .stButton button {
        background: linear-gradient(90deg, #4DB6AC, #80CBC4);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8em 1.6em;
        font-weight: 600;
        font-size: 1.05em;
        transition: 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #009688, #4DB6AC);
        transform: scale(1.05);
    }
    h2, h3, .streamlit-expanderHeader {
        color: #00695C !important;
        font-weight: 700 !important;
    }
    .streamlit-expanderHeader {
        background: rgba(224,242,241,0.6);
        border-radius: 10px;
        border: 1px solid rgba(0,150,136,0.2);
    }
    .stPyplot {
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
    }
    .result-box {
        background: rgba(224,242,241,0.9);
        border-radius: 15px;
        padding: 1rem;
        margin-top: 1rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        color: #004D40;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
    <div class="main-header">
        <h1>🏗 Beam Analysis App</h1>
        <h3>Analyze Bending Moment, Shear Force, Slope & Deflection for Various Beam Types</h3>
    </div>
""", unsafe_allow_html=True)

# ---------------- INPUT PANEL ----------------
st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
st.header("📐 Input Parameters")

col1, col2 = st.columns(2)
with col1:
    beam_length = st.number_input("Beam Length (m)", min_value=0.1, value=10.0, step=0.1)
    EI = st.number_input("Flexural Rigidity (EI)", min_value=0.0, value=2.0e8, step=1e6)
with col2:
    beam_type = st.selectbox("Beam Type", [
        "Simply Supported",
        "Continuous",
        "Cantilever",
        "Propped Cantilever",
        "Fixed"
    ])
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LOADS PANEL ----------------
st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
st.header("⚙ Add Loads")

# Point Loads
with st.expander("➕ Point Loads", expanded=True):
    num_point_loads = st.number_input("Number of Point Loads", min_value=0, value=1, step=1)
    point_loads = []
    for i in range(int(num_point_loads)):
        loc = st.number_input(f"Location of Point Load {i+1} (m)", min_value=0.0, value=beam_length/2, step=0.1, key=f"ploc_{i}")
        mag = st.number_input(f"Magnitude of Point Load {i+1} (kN)", min_value=0.0, value=10.0, step=0.1, key=f"pmag_{i}")
        point_loads.append((loc, mag))

# UDL
with st.expander("➕ Uniformly Distributed Loads (UDL)"):
    num_udls = st.number_input("Number of UDLs", min_value=0, value=0, step=1)
    udls = []
    for i in range(int(num_udls)):
        start = st.number_input(f"Start of UDL {i+1} (m)", min_value=0.0, value=0.0, step=0.1, key=f"ustart_{i}")
        end = st.number_input(f"End of UDL {i+1} (m)", min_value=0.0, value=beam_length, step=0.1, key=f"uend_{i}")
        intensity = st.number_input(f"Load Intensity of UDL {i+1} (kN/m)", min_value=0.0, value=5.0, step=0.1, key=f"uint_{i}")
        udls.append((start, end, intensity))

# Moments
with st.expander("➕ Moment Loads"):
    num_moments = st.number_input("Number of Moment Loads", min_value=0, value=0, step=1)
    moments = []
    for i in range(int(num_moments)):
        loc = st.number_input(f"Location of Moment {i+1} (m)", min_value=0.0, value=beam_length/2, step=0.1, key=f"mloc_{i}")
        mag = st.number_input(f"Magnitude of Moment {i+1} (kN·m)", value=10.0, step=0.1, key=f"mmag_{i}")
        moments.append((loc, mag))
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RUN ANALYSIS ----------------
st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
if st.button("🚀 Run Analysis"):
    st.success("✅ Beam Analysis Running...")

    x = np.linspace(0, beam_length, 500)
    shear = np.zeros_like(x)
    moment = np.zeros_like(x)

    total_load = 0
    moment_about_A = 0

    for loc, mag in point_loads:
        total_load += mag
        moment_about_A += mag * loc

    for start, end, w in udls:
        L = end - start
        load = w * L
        total_load += load
        moment_about_A += load * (start + L/2)

    for loc, mag in moments:
        moment_about_A -= mag

    RB = moment_about_A / beam_length
    RA = total_load - RB

    for i, xi in enumerate(x):
        V = RA
        M = RA * xi
        for loc, mag in point_loads:
            if xi >= loc:
                V -= mag
                M -= mag * (xi - loc)
        for start, end, w in udls:
            if xi > start:
                if xi <= end:
                    L = xi - start
                    V -= w * L
                    M -= w * L**2 / 2
                else:
                    L = end - start
                    V -= w * L
                    M -= w * L * (xi - start - L/2)
        for loc, mag in moments:
            if xi >= loc:
                M -= mag
        shear[i] = V
        moment[i] = M

    # --- SFD ---
    st.subheader("📊 Shear Force Diagram (SFD)")
    fig1, ax1 = plt.subplots()
    ax1.plot(x, shear, color="#26A69A", linewidth=3)
    ax1.fill_between(x, 0, shear, color="#B2DFDB", alpha=0.6)
    ax1.axhline(0, color="black")
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel("Beam Length (m)")
    ax1.set_ylabel("Shear Force (kN)")
    st.pyplot(fig1)

    # --- BMD ---
    st.subheader("📈 Bending Moment Diagram (BMD)")
    fig2, ax2 = plt.subplots()
    ax2.plot(x, moment, color="#81C784", linewidth=3)
    ax2.fill_between(x, 0, moment, color="#C8E6C9", alpha=0.6)
    ax2.axhline(0, color="black")
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel("Beam Length (m)")
    ax2.set_ylabel("Bending Moment (kN·m)")
    st.pyplot(fig2)

    # --- Slope & Deflection ---
    st.subheader("📐 Slope and Deflection")

    dx = x[1] - x[0]
    slope = np.cumsum(moment / EI) * dx
    deflection = np.cumsum(slope) * dx
    deflection_mm = deflection * 1000  # convert to mm

    max_deflection = np.min(deflection_mm)
    slope_left = slope[0]
    slope_right = slope[-1]

    # Text output
    st.markdown(f"""
    <div class="result-box">
        <b>Slope at Left Support:</b> {slope_left:.6e} radians<br>
        <b>Slope at Right Support:</b> {slope_right:.6e} radians<br>
        <b>Maximum Deflection:</b> {abs(max_deflection):.4f} mm
    </div>
    """, unsafe_allow_html=True)

    # --- Slope Diagram ---
    st.subheader("📉 Slope Diagram")
    fig3, ax3 = plt.subplots()
    ax3.plot(x, slope, color="#4FC3F7", linewidth=3)
    ax3.fill_between(x, 0, slope, color="#B3E5FC", alpha=0.6)
    ax3.axhline(0, color="black")
    ax3.grid(True, alpha=0.3)
    ax3.set_xlabel("Beam Length (m)")
    ax3.set_ylabel("Slope (radians)")
    st.pyplot(fig3)

    # --- Deflection Diagram ---
    st.subheader("🏗 Deflection Diagram")
    fig4, ax4 = plt.subplots()
    ax4.plot(x, deflection_mm, color="#FFB74D", linewidth=3)
    ax4.fill_between(x, 0, deflection_mm, color="#FFE0B2", alpha=0.6)
    ax4.axhline(0, color="black")
    ax4.grid(True, alpha=0.3)
    ax4.set_xlabel("Beam Length (m)")
    ax4.set_ylabel("Deflection (mm)")
    st.pyplot(fig4)

    st.success(f"✅ Completed | Reactions: RA = {RA:.2f} kN, RB = {RB:.2f} kN")

st.markdown("</div>", unsafe_allow_html=True)

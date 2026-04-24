import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Plasticity Visualizer", layout="centered")

st.title("Spread of Plasticity in a Rectangular Beam")
st.markdown("This interactive tool demonstrates how a steel cross-section transitions from an elastic state to a fully plastic state, defining the **Shape Factor**.")

# --- Sidebar Inputs ---
st.sidebar.header("Section Properties")
b = st.sidebar.number_input("Width, b (mm)", min_value=10.0, value=100.0, step=10.0)
h = st.sidebar.number_input("Depth, h (mm)", min_value=10.0, value=200.0, step=10.0)
fy = st.sidebar.number_input("Yield Stress, fy (MPa)", min_value=100.0, value=250.0, step=10.0)

# --- Calculate Capacities ---
# Elastic Moment (My) and Plastic Moment (Mp)
My = (fy * b * (h**2)) / 6.0  # N-mm
Mp = (fy * b * (h**2)) / 4.0  # N-mm

My_kNm = My / 1e6
Mp_kNm = Mp / 1e6

# Display calculated capacities in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Theoretical Capacities")
st.sidebar.markdown(f"**Elastic Moment ($M_y$):** {My_kNm:.2f} kNm")
st.sidebar.markdown(f"**Plastic Moment ($M_p$):** {Mp_kNm:.2f} kNm")
st.sidebar.markdown(f"**Shape Factor ($S$):** {Mp/My:.2f}")

# --- Main App Interface ---
# The primary slider for applied bending moment
M_kNm = st.slider("Applied Bending Moment (kNm)", min_value=0.0, max_value=float(Mp_kNm), value=0.0, step=0.1)
M = M_kNm * 1e6  # Convert back to N-mm for calculations

# --- Mathematical Logic ---
y_vals = np.linspace(-h/2, h/2, 500)
stress_vals = np.zeros_like(y_vals)

if M <= My:
    # Phase 1: Fully Elastic
    state = "Fully Elastic"
    ye = h / 2
    sigma_max = (M / My) * fy if My > 0 else 0
    stress_vals = (y_vals / ye) * sigma_max if ye > 0 else 0
else:
    # Phase 2 & 3: Elasto-Plastic or Fully Plastic
    M = min(M, Mp) # Cap the moment at Mp
    state = "Elasto-Plastic" if M < Mp else "Fully Plastic (Mechanism)"
    
    # Calculate depth of the remaining elastic core
    ye_squared = 0.75 * (h**2) - (3 * M) / (fy * b)
    ye = np.sqrt(max(0, ye_squared))
    
    # Build the stress profile
    for i, y in enumerate(y_vals):
        if y < -ye:
            stress_vals[i] = -fy  # Compression yielding
        elif y > ye:
            stress_vals[i] = fy   # Tension yielding
        else:
            stress_vals[i] = (y / ye) * fy if ye > 0 else np.sign(y) * fy

# --- Display Metrics ---
st.info(f"**Current Structural State:** {state} | **Remaining Elastic Core Depth:** {2*ye:.1f} mm")

# --- Matplotlib Plotting ---
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the stress line
ax.plot(stress_vals, y_vals, color='red', linewidth=2)

# Shade the tension and compression zones
ax.fill_betweenx(y_vals, 0, stress_vals, where=(stress_vals > 0), color='salmon', alpha=0.5, label='Tension (+)')
ax.fill_betweenx(y_vals, 0, stress_vals, where=(stress_vals < 0), color='lightblue', alpha=0.5, label='Compression (-)')

# Reference lines
ax.axvline(0, color='black', linewidth=1.5)
ax.axhline(0, color='black', linestyle='--', linewidth=1.5, label='Neutral Axis')
ax.axhline(ye, color='gray', linestyle=':', linewidth=1)
ax.axhline(-ye, color='gray', linestyle=':', linewidth=1)

# Formatting
ax.set_xlim(-fy * 1.5, fy * 1.5)
ax.set_ylim(-h/2 - 20, h/2 + 20)
ax.set_xlabel('Stress (MPa)')
ax.set_ylabel('Distance from Neutral Axis (mm)')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

# Render the plot in Streamlit
st.pyplot(fig)

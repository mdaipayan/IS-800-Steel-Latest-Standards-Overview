import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.title("Spread of Plasticity in a Rectangular Beam")
st.write("Adjust the slider to see how the stress block changes from purely elastic to fully plastic.")

# Interactive Sliders
depth = st.slider("Beam Depth (mm)", min_value=100, max_value=500, value=300)
fy = st.slider("Yield Stress, $f_y$ (MPa)", min_value=250, max_value=550, value=250, step=10)
# Slider to control how far yielding has penetrated (0 = elastic, 1 = fully plastic)
yield_penetration = st.slider("Yield Penetration", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

# Calculate parameters
c = depth / 2  # Distance to extreme fiber
elastic_core = c * (1 - yield_penetration) # Depth of the remaining elastic core

# Y-coordinates for plotting
y_vals = np.linspace(-c, c, 500)
stress_vals = np.zeros_like(y_vals)

# Define the stress profile
for i, y in enumerate(y_vals):
    if abs(y) <= elastic_core:
        # Elastic region (linear)
        stress_vals[i] = (y / elastic_core) * fy if elastic_core > 0 else np.sign(y) * fy
    else:
        # Plastic region (constant yield stress)
        stress_vals[i] = np.sign(y) * fy

# Plotting
fig, ax = plt.subplots(figsize=(6, 8))
ax.plot(stress_vals, y_vals, color='red', linewidth=2)
ax.fill_betweenx(y_vals, 0, stress_vals, where=(stress_vals > 0), color='salmon', alpha=0.5, label='Tension')
ax.fill_betweenx(y_vals, 0, stress_vals, where=(stress_vals < 0), color='lightblue', alpha=0.5, label='Compression')

# Formatting the plot
ax.axvline(0, color='black', linewidth=1)
ax.axhline(0, color='black', linestyle='--', linewidth=1, label='Neutral Axis')
ax.set_xlim(-fy * 1.5, fy * 1.5)
ax.set_ylim(-c - 20, c + 20)
ax.set_ylabel("Distance from Neutral Axis (mm)")
ax.set_xlabel("Stress (MPa)")
ax.set_title("Stress Block Profile")
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)

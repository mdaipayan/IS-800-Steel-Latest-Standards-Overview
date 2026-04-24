import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --- 1. Define Beam Properties ---
b = 100.0  # Width of the rectangular section in mm
h = 200.0  # Total height of the section in mm
fy = 250.0 # Yield stress of the steel in MPa (N/mm^2)

# --- 2. Calculate Capacities ---
# Elastic Moment Capacity (My = fy * Ze)
My = (fy * b * (h**2)) / 6.0  # Result in N-mm

# Plastic Moment Capacity (Mp = fy * Zp)
Mp = (fy * b * (h**2)) / 4.0  # Result in N-mm

# Convert to kNm for a cleaner UI display
My_kNm = My / 1e6
Mp_kNm = Mp / 1e6

# --- 3. Setup the Matplotlib Figure ---
fig, ax = plt.subplots(figsize=(8, 6))
plt.subplots_adjust(left=0.20, bottom=0.30) # Make room for the slider

ax.set_xlim(-fy * 1.5, fy * 1.5)
ax.set_ylim(-h/2 - 20, h/2 + 20)
ax.set_xlabel('Stress (MPa)')
ax.set_ylabel('Distance from Neutral Axis (mm)')
ax.set_title('Spread of Plasticity in a Rectangular Beam')

# Draw neutral axis and center vertical line
ax.axvline(0, color='black', linewidth=1)
ax.axhline(0, color='black', linestyle='--', linewidth=1, label='Neutral Axis')
ax.legend(loc='upper right')

# Initialize the plot line and text
line, = ax.plot([], [], 'r-', lw=2)
status_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, verticalalignment='top', 
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# --- 4. Setup the Interactive Slider ---
ax_moment = plt.axes([0.20, 0.15, 0.65, 0.03])
slider_moment = Slider(
    ax=ax_moment,
    label='Applied\nMoment\n(kNm)',
    valmin=0,
    valmax=Mp_kNm,
    valinit=0,
    color='gray'
)

# --- 5. Define the Mathematical Update Logic ---
def update(val):
    # Get current slider value and convert back to N-mm
    M_kNm = slider_moment.val
    M = M_kNm * 1e6  
    
    # Create an array of Y-coordinates (depth of the beam)
    y_vals = np.linspace(-h/2, h/2, 500)
    stress_vals = np.zeros_like(y_vals)
    
    if M <= My:
        # PHASE 1: Fully Elastic
        state = "State: Fully Elastic"
        sigma_max = (M / My) * fy
        ye = h / 2  # The entire half-depth is elastic
        
        # Stress varies linearly from top to bottom
        stress_vals = (y_vals / ye) * sigma_max
        
    else:
        # PHASE 2 & 3: Elasto-Plastic or Fully Plastic
        # Prevent floating point errors from pushing M slightly above Mp
        M = min(M, Mp) 
        state = "State: Elasto-Plastic" if M < Mp else "State: Fully Plastic (Mechanism)"
        
        # Calculate depth of the remaining elastic core (ye)
        # Derived from equilibrium equation: M = fy * b * (h^2/4 - ye^2/3)
        ye_squared = 0.75 * (h**2) - (3 * M) / (fy * b)
        ye = np.sqrt(max(0, ye_squared)) 
        
        # Build the stress profile
        for i, y in enumerate(y_vals):
            if y < -ye:
                stress_vals[i] = -fy  # Top fibers yielded in compression
            elif y > ye:
                stress_vals[i] = fy   # Bottom fibers yielded in tension
            else:
                # Linear elastic core
                stress_vals[i] = (y / ye) * fy if ye > 0 else np.sign(y) * fy
                
    # Update the line data
    line.set_data(stress_vals, y_vals)
    
    # Update the shaded areas (requires removing old patches and drawing new ones)
    [c.remove() for c in ax.collections]
    ax.fill_betweenx(y_vals, 0, stress_vals, where=(stress_vals > 0), color='salmon', alpha=0.5)
    ax.fill_betweenx(y_vals, 0, stress_vals, where=(stress_vals < 0), color='lightblue', alpha=0.5)
    
    # Update the informational text
    status_text.set_text(f'{state}\n'
                         f'Elastic Core Depth: {2*ye:.1f} mm\n'
                         f'My = {My_kNm:.1f} kNm\n'
                         f'Mp = {Mp_kNm:.1f} kNm')
    fig.canvas.draw_idle()

# --- 6. Connect Slider and Execute ---
slider_moment.on_changed(update)
update(0) # Call update once to initialize the plot at 0 kNm
plt.show()

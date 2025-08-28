import numpy as np
import matplotlib.pyplot as plt

# Function to draw a circle
def draw_circle(center, radius, points=100):
    angles = np.linspace(0, 2 * np.pi, points)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return x, y

# Original circle
center = (0, 0)
radius = 5
x, y = draw_circle(center, radius)

# Translation
tx, ty = 3, 2
x_trans = x + tx
y_trans = y + ty

# Rotation (about origin)
theta = np.radians(45)  # 45 degrees
x_rot = x * np.cos(theta) - y * np.sin(theta)
y_rot = x * np.sin(theta) + y * np.cos(theta)

# Scaling
sx, sy = 1.5, 0.5
x_scale = center[0] + sx * (x - center[0])
y_scale = center[1] + sy * (y - center[1])

# Shearing (in x-direction)
shear_factor = 0.5
x_shear = x + shear_factor * y
y_shear = y

# Reflection (across y-axis)
x_refl = -x
y_refl = y

# Plotting
plt.figure(figsize=(6,6))
plt.plot(x, y, label="Original Circle")
plt.plot(x_trans, y_trans, label="Translated")
plt.plot(x_rot, y_rot, label="Rotated")
plt.plot(x_scale, y_scale, label="Scaled")
plt.plot(x_shear, y_shear, label="Sheared")
plt.plot(x_refl, y_refl, label="Reflected")

plt.gca().set_aspect('equal', adjustable='box')
plt.legend()
plt.title("Circle Transformations")
plt.grid(True)
plt.show()


# aim to assignment
# objective


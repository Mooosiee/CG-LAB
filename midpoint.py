import matplotlib.pyplot as plt

def midpoint_circle(center, radius):
    x0, y0 = center
    x = radius
    y = 0
    p = 1 - radius  # Initial decision parameter
    points = []

    # Plot initial points (on axis)
    points.append((x0 + x, y0))  # Right
    points.append((x0 - x, y0))  # Left
    points.append((x0, y0 + radius))  # Top
    points.append((x0, y0 - radius))  # Bottom

    while x > y:
        y += 1
        if p <= 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * y - 2 * x + 1
        
        # Plot points symmetrically
        points.append((x0 + x, y0 + y))
        points.append((x0 - x, y0 + y))
        points.append((x0 + x, y0 - y))
        points.append((x0 - x, y0 - y))
        points.append((x0 + y, y0 + x))
        points.append((x0 - y, y0 + x))
        points.append((x0 + y, y0 - x))
        points.append((x0 - y, y0 - x))

    return points

# Plotting the Mid-point Circle Algorithm
center = (0, 0)
radius = 20
points_midpoint = midpoint_circle(center, radius)

# Extract X and Y coordinates for plotting
x_vals_midpoint = [pt[0] for pt in points_midpoint]
y_vals_midpoint = [pt[1] for pt in points_midpoint]

plt.figure(figsize=(6,6))
plt.scatter(x_vals_midpoint, y_vals_midpoint, color='blue', s=1)
plt.title("Mid-point Circle Algorithm")
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True)
plt.show()

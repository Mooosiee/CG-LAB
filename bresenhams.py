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

def bresenham_circle(center, radius):
    x0, y0 = center
    x = radius
    y = 0
    p = 3 - 2 * radius  # Initial decision parameter
    points = []

    # Plot initial points (on axis)
    points.append((x0 + x, y0))
    points.append((x0 - x, y0))
    points.append((x0, y0 + radius))
    points.append((x0, y0 - radius))

    while x > y:
        y += 1
        if p <= 0:
            p = p + 4 * y + 6
        else:
            x -= 1
            p = p + 4 * (y - x) + 10
        
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

# Define the center and radius
center = (0, 0)
radius = 20

# Plotting the Mid-point Circle Algorithm
points_midpoint = midpoint_circle(center, radius)
x_vals_midpoint = [pt[0] for pt in points_midpoint]
y_vals_midpoint = [pt[1] for pt in points_midpoint]

plt.figure(figsize=(6,6))
plt.scatter(x_vals_midpoint, y_vals_midpoint, color='blue', s=1)
plt.title("Mid-point Circle Algorithm")
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True)
plt.show()

# Plotting the Bresenham Circle Algorithm
points_bresenham = bresenham_circle(center, radius)
x_vals_bresenham = [pt[0] for pt in points_bresenham]
y_vals_bresenham = [pt[1] for pt in points_bresenham]

plt.figure(figsize=(6,6))
plt.scatter(x_vals_bresenham, y_vals_bresenham, color='red', s=1)
plt.title("Bresenham Circle Algorithm")
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True)
plt.show()

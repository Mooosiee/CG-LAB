import matplotlib.pyplot as plt

def dda(x1, y1, x2, y2):
    points = []
    dx = x2 - x1
    dy = y2 - y1
    
    steps = max(abs(dx), abs(dy))
    
    x_inc = dx / steps
    y_inc = dy / steps
    
    x = x1
    y = y1
    for _ in range(int(steps) + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    
    return points

def bresenham(x1, y1, x2, y2):
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1
    
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    
    if dx > dy:
        err = dx // 2
        while x != x2:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy // 2
        while y != y2:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x2, y2))
    return points

# Input points
x1, y1 = map(int, input("Enter x1 y1: ").split())
x2, y2 = map(int, input("Enter x2 y2: ").split())

# Generate points using both algorithms
dda_points = dda(x1, y1, x2, y2)
bres_points = bresenham(x1, y1, x2, y2)

# Plotting
plt.figure(figsize=(8, 8))
plt.title("DDA vs Bresenham Line Drawing Algorithms")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.grid(True)

# Plot DDA points
dda_x, dda_y = zip(*dda_points)
plt.plot(dda_x, dda_y, 'ro-', label="DDA")

# Plot Bresenham points
bres_x, bres_y = zip(*bres_points)
plt.plot(bres_x, bres_y, 'bo-', label="Bresenham")

plt.legend()
plt.show()

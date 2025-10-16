import pygame
import sys
import time
from collections import deque
import random

# Configuration
WIDTH, HEIGHT = 1000, 600
CANVAS_WIDTH = 700
PANEL_WIDTH = WIDTH - CANVAS_WIDTH

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
LIGHT_GRAY = (100, 100, 100)
PURPLE = (128, 0, 128) # For temporary highlights
TEAL = (0, 128, 128)   # For scanline active

# Predefined Polygons (centered and scaled for the canvas)
def get_polygon_vertices(shape_name, canvas_width, canvas_height):
    center_x = canvas_width // 2
    center_y = canvas_height // 2
    
    if shape_name == "Triangle":
        size = 150
        return [
            (center_x, center_y - size),
            (center_x - size, center_y + size),
            (center_x + size, center_y + size)
        ]
    elif shape_name == "Square":
        size = 120
        return [
            (center_x - size, center_y - size),
            (center_x + size, center_y - size),
            (center_x + size, center_y + size),
            (center_x - size, center_y + size)
        ]
    elif shape_name == "Star":
        # A 5-pointed star
        outer_radius = 180
        inner_radius = 70
        points = []
        for i in range(5):
            angle = i * 2 * 3.14159 / 5 - 3.14159 / 2 # Start at top
            points.append((int(center_x + outer_radius * pygame.math.Vector2(0, -1).rotate_rad(angle).x),
                           int(center_y + outer_radius * pygame.math.Vector2(0, -1).rotate_rad(angle).y)))
            angle += 3.14159 / 5
            points.append((int(center_x + inner_radius * pygame.math.Vector2(0, -1).rotate_rad(angle).x),
                           int(center_y + inner_radius * pygame.math.Vector2(0, -1).rotate_rad(angle).y)))
        return points
    elif shape_name == "Hexagon":
        radius = 150
        points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = 3.14159 / 180 * angle_deg
            points.append((int(center_x + radius * pygame.math.Vector2(0, -1).rotate_rad(angle_rad).x),
                           int(center_y + radius * pygame.math.Vector2(0, -1).rotate_rad(angle_rad).y)))
        return points
    return []

PREDEFINED_POLYGONS = {
    'T': 'Triangle',
    'S': 'Square',
    'A': 'Star', # 'A' for A-star :)
    'H': 'Hexagon'
}

def generate_noise_background(surface, density=0.01):
    """Adds subtle random noise to a surface."""
    w, h = surface.get_size()
    for _ in range(int(w * h * density)):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        # Subtle light gray or dark gray dots
        color = random.choice([LIGHT_GRAY, GRAY])
        surface.set_at((x, y), color)


def visualize_scanline(screen, polygon, fill_color, boundary_color, speed=5):
    """Visualize Scanline Fill step by step with clear animation"""
    if len(polygon) < 3:
        return 0
    
    pixels = 0
    min_y = min(p[1] for p in polygon)
    max_y = max(p[1] for p in polygon)
    
    # Store original state for clearing scanline, if needed, or draw directly
    
    for y in range(min_y, max_y + 1):
        # Draw current scanline in a temporary color (TEAL)
        pygame.draw.line(screen, TEAL, (0, y), (CANVAS_WIDTH, y), 1)
        pygame.display.flip()
        pygame.time.delay(speed * 2) # Slightly longer delay for scanline draw

        intersections = []
        
        # Find intersections
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]
            
            if p1[1] != p2[1]: # Not a horizontal line
                # Check if scanline crosses the edge
                if min(p1[1], p2[1]) <= y < max(p1[1], p2[1]):
                    # Calculate x-coordinate of intersection
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(int(x))
        
        intersections.sort()
        
        # Fill between pairs with animation
        for i in range(0, len(intersections) - 1, 2):
            for x in range(intersections[i], intersections[i + 1] + 1):
                if 0 <= x < CANVAS_WIDTH and 0 <= y < HEIGHT:
                    # Animate pixel by pixel filling
                    screen.set_at((x, y), fill_color)
                    pixels += 1
                    if pixels % 20 == 0: # Update screen every few pixels for smoother animation
                        pygame.display.flip()
                        pygame.time.delay(speed // 2)

        # After filling a row, clear the temporary scanline color by redrawing
        # the background or previous pixel color (too complex). Instead,
        # we'll just overwrite it with the fill color where applicable.
        # For professional visualizations, a separate buffer would be used.
        # Here, the fill color will naturally cover the scanline.
    
    return pixels


def visualize_flood_fill_4(screen, x, y, target_color, fill_color, boundary_color, speed=1):
    """Visualize 4-connected Flood Fill with step-by-step animation"""
    if x < 0 or x >= CANVAS_WIDTH or y < 0 or y >= HEIGHT:
        return 0
    
    start_pixel_color = screen.get_at((x, y))[:3]
    if start_pixel_color != target_color:
        return 0
    if target_color == fill_color or start_pixel_color == fill_color: # Already filled or trying to fill with same color
        return 0
    if start_pixel_color == boundary_color: # Don't fill boundary
        return 0
    
    pixels = 0
    queue = deque([(x, y)])
    visited = set([(x, y)]) # Use visited set for cleaner fill and avoiding re-adds
    
    # Pre-draw the polygon boundary to ensure it's not part of the target color
    # (This is handled by the `reset_canvas_with_shape` and `main` loop)

    while queue:
        cx, cy = queue.popleft()
        
        # Check current pixel color
        current_pixel_color = screen.get_at((cx, cy))[:3]

        if current_pixel_color == target_color:
            # Temporarily highlight the pixel being processed
            screen.set_at((cx, cy), PURPLE) 
            pygame.display.flip()
            pygame.time.delay(speed)
            
            # Fill the pixel
            screen.set_at((cx, cy), fill_color)
            pixels += 1
            
            # Add neighbors if they haven't been visited and are the target color
            neighbors = [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
            for nx, ny in neighbors:
                if 0 <= nx < CANVAS_WIDTH and 0 <= ny < HEIGHT and \
                   (nx, ny) not in visited and \
                   screen.get_at((nx, ny))[:3] == target_color:
                    queue.append((nx, ny))
                    visited.add((nx, ny)) # Mark as visited when added to queue
    return pixels


def visualize_flood_fill_8(screen, x, y, target_color, fill_color, boundary_color, speed=1):
    """Visualize 8-connected Flood Fill"""
    if x < 0 or x >= CANVAS_WIDTH or y < 0 or y >= HEIGHT:
        return 0

    start_pixel_color = screen.get_at((x, y))[:3]
    if start_pixel_color != target_color:
        return 0
    if target_color == fill_color or start_pixel_color == fill_color:
        return 0
    if start_pixel_color == boundary_color:
        return 0

    pixels = 0
    queue = deque([(x, y)])
    visited = set([(x, y)])
    
    while queue:
        cx, cy = queue.popleft()

        current_pixel_color = screen.get_at((cx, cy))[:3]

        if current_pixel_color == target_color:
            screen.set_at((cx, cy), PURPLE)
            pygame.display.flip()
            pygame.time.delay(speed)
            
            screen.set_at((cx, cy), fill_color)
            pixels += 1
            
            # 8 neighbors
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < CANVAS_WIDTH and 0 <= ny < HEIGHT and \
                           (nx, ny) not in visited and \
                           screen.get_at((nx, ny))[:3] == target_color:
                            queue.append((nx, ny))
                            visited.add((nx, ny))
    return pixels


def visualize_boundary_fill(screen, x, y, boundary_color, fill_color, speed=1):
    """Visualize Boundary Fill with step-by-step animation"""
    if x < 0 or x >= CANVAS_WIDTH or y < 0 or y >= HEIGHT:
        return 0
    
    start_pixel_color = screen.get_at((x, y))[:3]
    if start_pixel_color == boundary_color or start_pixel_color == fill_color:
        return 0
    
    pixels = 0
    stack = [(x, y)]
    visited = set([(x, y)])

    while stack:
        cx, cy = stack.pop()
        
        # Check current pixel color
        current_pixel_color = screen.get_at((cx, cy))[:3]
        
        if current_pixel_color == boundary_color or current_pixel_color == fill_color:
            continue
        
        # Highlight current pixel being processed
        screen.set_at((cx, cy), PURPLE)
        pygame.display.flip()
        pygame.time.delay(speed)

        screen.set_at((cx, cy), fill_color)
        pixels += 1
        
        # Add neighbors
        neighbors = [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
        for nx, ny in neighbors:
            if 0 <= nx < CANVAS_WIDTH and 0 <= ny < HEIGHT and \
               (nx, ny) not in visited: # Only check boundary/fill color on pop
                stack.append((nx, ny))
                visited.add((nx, ny)) # Mark as visited when added to stack
    return pixels


def draw_polygon(screen, vertices, color, width=2):
    """Draw polygon outline"""
    if len(vertices) < 2:
        return
    pygame.draw.polygon(screen, color, vertices, width) # Use pygame.draw.polygon for clean outline


def get_center(vertices):
    """Get center point of polygon (approximate for flood fill seed)"""
    if not vertices:
        return None
    min_x = min(v[0] for v in vertices)
    max_x = max(v[0] for v in vertices)
    min_y = min(v[1] for v in vertices)
    max_y = max(v[1] for v in vertices)
    
    # Try to find a point guaranteed to be inside for convex polygons
    # For complex polygons, this might still be outside. For robustness,
    # we could use a ray casting approach to find an interior point.
    # For now, simply average the vertices.
    cx = sum(v[0] for v in vertices) // len(vertices)
    cy = sum(v[1] for v in vertices) // len(vertices)

    # Basic check: move slightly if it falls on a boundary for flood fill
    # (This is a simplified approach, a proper point-in-polygon test is better)
    if pygame.Surface.get_at(pygame.display.get_surface(), (cx, cy))[:3] == BLACK:
        # Check surrounding pixels if the center happens to be exactly on the boundary
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                test_x, test_y = cx + dx, cy + dy
                if 0 <= test_x < CANVAS_WIDTH and 0 <= test_y < HEIGHT and \
                   pygame.Surface.get_at(pygame.display.get_surface(), (test_x, test_y))[:3] == BLACK:
                    return (test_x, test_y)

    return (cx, cy)


def reset_canvas_with_shape(screen, current_polygon_vertices, border_color=WHITE):
    """Clears canvas, adds noise, and draws the selected polygon."""
    canvas_rect = pygame.Rect(0, 0, CANVAS_WIDTH, HEIGHT)
    canvas_surface = pygame.Surface(canvas_rect.size)
    canvas_surface.fill(BLACK)
    generate_noise_background(canvas_surface, density=0.005) # Add subtle noise
    screen.blit(canvas_surface, (0, 0)) # Blit to main screen
    
    draw_polygon(screen, current_polygon_vertices, border_color)
    pygame.display.flip()

def draw_panel(screen, font, vertices, mode, result, current_shape_name):
    """Draw control panel"""
    panel_x = CANVAS_WIDTH
    pygame.draw.rect(screen, GRAY, (panel_x, 0, PANEL_WIDTH, HEIGHT))
    
    y = 20
    
    title = font.render("Polygon Fill Visualizer", True, YELLOW)
    screen.blit(title, (panel_x + 10, y))
    y += 40
    
    # Pre-defined shape instructions
    shape_instr = [
        "SELECT SHAPE:",
        "T - Triangle",
        "S - Square",
        "A - Star",
        "H - Hexagon",
        "",
        f"Current Shape: {current_shape_name if current_shape_name else 'None'}",
        "",
        "SELECT ALGORITHM:",
        "1 - Scanline (Green)",
        "2 - Flood Fill 4-conn (Blue)",
        "3 - Flood Fill 8-conn (Magenta)",
        "4 - Boundary Fill (Orange, Red Border)",
        "",
        "C - Clear Canvas",
        # "SPACE - Pause/Resume (if applicable)",
        "",
        f"Vertices: {len(vertices)}",
        f"Status: {mode}"
    ]
    
    for line in shape_instr:
        text = font.render(line, True, WHITE)
        screen.blit(text, (panel_x + 10, y))
        y += 25
    
    if result:
        y += 20
        screen.blit(font.render("LAST RESULT:", True, YELLOW), (panel_x + 10, y))
        y += 30
        screen.blit(font.render(result[0], True, YELLOW), (panel_x + 10, y))
        y += 25
        screen.blit(font.render(f"Pixels: {result[1]:,}", True, WHITE), (panel_x + 10, y))
        y += 25
        screen.blit(font.render(f"Time: {result[2]:.4f}s", True, WHITE), (panel_x + 10, y))
        y += 25
        if result[1] > 0:
            speed_per_pixel = (result[2] / result[1]) * 1_000_000 if result[1] > 0 else 0
            screen.blit(font.render(f"Avg. {speed_per_pixel:.2f} µs/px", True, WHITE), (panel_x + 10, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Professional Polygon Fill Algorithms Visualizer")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 20)
    
    current_polygon_vertices = []
    current_shape_name = None
    mode = "Select a shape (T, S, A, H)"
    result = None
    running = True
    
    # Initial clear and noise
    canvas_surface = pygame.Surface((CANVAS_WIDTH, HEIGHT))
    canvas_surface.fill(BLACK)
    generate_noise_background(canvas_surface, density=0.005)
    screen.blit(canvas_surface, (0, 0))
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    # Clear everything
                    canvas_surface.fill(BLACK)
                    generate_noise_background(canvas_surface, density=0.005)
                    screen.blit(canvas_surface, (0, 0))
                    current_polygon_vertices = []
                    current_shape_name = None
                    mode = "Select a shape (T, S, A, H)"
                    result = None
                
                elif event.key == pygame.K_t:
                    current_shape_name = PREDEFINED_POLYGONS['T']
                    current_polygon_vertices = get_polygon_vertices(current_shape_name, CANVAS_WIDTH, HEIGHT)
                    reset_canvas_with_shape(screen, current_polygon_vertices, WHITE)
                    mode = f"Shape: {current_shape_name} - Ready"
                    result = None
                
                elif event.key == pygame.K_s:
                    current_shape_name = PREDEFINED_POLYGONS['S']
                    current_polygon_vertices = get_polygon_vertices(current_shape_name, CANVAS_WIDTH, HEIGHT)
                    reset_canvas_with_shape(screen, current_polygon_vertices, WHITE)
                    mode = f"Shape: {current_shape_name} - Ready"
                    result = None

                elif event.key == pygame.K_a: # For star
                    current_shape_name = PREDEFINED_POLYGONS['A']
                    current_polygon_vertices = get_polygon_vertices(current_shape_name, CANVAS_WIDTH, HEIGHT)
                    reset_canvas_with_shape(screen, current_polygon_vertices, WHITE)
                    mode = f"Shape: {current_shape_name} - Ready"
                    result = None

                elif event.key == pygame.K_h: # For hexagon
                    current_shape_name = PREDEFINED_POLYGONS['H']
                    current_polygon_vertices = get_polygon_vertices(current_shape_name, CANVAS_WIDTH, HEIGHT)
                    reset_canvas_with_shape(screen, current_polygon_vertices, WHITE)
                    mode = f"Shape: {current_shape_name} - Ready"
                    result = None

                # Algorithm selection
                if current_polygon_vertices: # Only allow algo selection if a shape is drawn
                    if event.key == pygame.K_1:  # Scanline
                        reset_canvas_with_shape(screen, current_polygon_vertices, WHITE) # Re-draw for clean start
                        mode = "Visualizing Scanline..."
                        
                        start = time.time()
                        pixels = visualize_scanline(screen, current_polygon_vertices, GREEN, WHITE, speed=5)
                        duration = time.time() - start
                        
                        draw_polygon(screen, current_polygon_vertices, WHITE) # Ensure border is visible after fill
                        pygame.display.flip()
                        
                        mode = "Scanline Complete"
                        result = ("Scanline Fill", pixels, duration)
                    
                    elif event.key == pygame.K_2:  # Flood 4
                        reset_canvas_with_shape(screen, current_polygon_vertices, WHITE)
                        center = get_center(current_polygon_vertices)
                        if center:
                            mode = "Visualizing Flood 4..."
                            start = time.time()
                            pixels = visualize_flood_fill_4(screen, center[0], center[1], BLACK, BLUE, WHITE, speed=1)
                            duration = time.time() - start
                            draw_polygon(screen, current_polygon_vertices, WHITE)
                            pygame.display.flip()
                            mode = "Flood 4 Complete"
                            result = ("Flood Fill 4-connected", pixels, duration)
                        else:
                            mode = "Error: Cannot find center for Flood Fill."
                    
                    elif event.key == pygame.K_3:  # Flood 8
                        reset_canvas_with_shape(screen, current_polygon_vertices, WHITE)
                        center = get_center(current_polygon_vertices)
                        if center:
                            mode = "Visualizing Flood 8..."
                            start = time.time()
                            pixels = visualize_flood_fill_8(screen, center[0], center[1], BLACK, MAGENTA, WHITE, speed=1)
                            duration = time.time() - start
                            draw_polygon(screen, current_polygon_vertices, WHITE)
                            pygame.display.flip()
                            mode = "Flood 8 Complete"
                            result = ("Flood 8 Complete", pixels, duration)
                        else:
                            mode = "Error: Cannot find center for Flood Fill."
                    
                    elif event.key == pygame.K_4:  # Boundary
                        # Boundary fill needs a different border color for visualization
                        reset_canvas_with_shape(screen, current_polygon_vertices, RED) # Use RED boundary
                        center = get_center(current_polygon_vertices)
                        if center:
                            mode = "Visualizing Boundary Fill..."
                            start = time.time()
                            pixels = visualize_boundary_fill(screen, center[0], center[1], RED, ORANGE, speed=1)
                            duration = time.time() - start
                            draw_polygon(screen, current_polygon_vertices, RED) # Ensure RED border is visible
                            pygame.display.flip()
                            mode = "Boundary Fill Complete"
                            result = ("Boundary Fill", pixels, duration)
                        else:
                            mode = "Error: Cannot find center for Boundary Fill."

        # Draw panel
        draw_panel(screen, font, current_polygon_vertices, mode, result, current_shape_name)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
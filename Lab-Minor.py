import pygame
import math
import numpy as np
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

class Vector3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def normalize(self):
        magnitude = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if magnitude > 0:
            return Vector3D(self.x/magnitude, self.y/magnitude, self.z/magnitude)
        return Vector3D(0, 0, 0)

class Matrix4x4:
    def __init__(self):
        self.m = [[0 for _ in range(4)] for _ in range(4)]
        # Initialize as identity matrix
        for i in range(4):
            self.m[i][i] = 1.0
    
    @staticmethod
    def translation(tx, ty, tz):
        matrix = Matrix4x4()
        matrix.m[0][3] = tx
        matrix.m[1][3] = ty
        matrix.m[2][3] = tz
        return matrix
    
    @staticmethod
    def rotation_x(angle):
        matrix = Matrix4x4()
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        matrix.m[1][1] = cos_a
        matrix.m[1][2] = -sin_a
        matrix.m[2][1] = sin_a
        matrix.m[2][2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_y(angle):
        matrix = Matrix4x4()
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        matrix.m[0][0] = cos_a
        matrix.m[0][2] = sin_a
        matrix.m[2][0] = -sin_a
        matrix.m[2][2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_z(angle):
        matrix = Matrix4x4()
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        matrix.m[0][0] = cos_a
        matrix.m[0][1] = -sin_a
        matrix.m[1][0] = sin_a
        matrix.m[1][1] = cos_a
        return matrix
    
    @staticmethod
    def scaling(sx, sy, sz):
        matrix = Matrix4x4()
        matrix.m[0][0] = sx
        matrix.m[1][1] = sy
        matrix.m[2][2] = sz
        return matrix
    
    def multiply(self, other):
        result = Matrix4x4()
        for i in range(4):
            for j in range(4):
                result.m[i][j] = 0
                for k in range(4):
                    result.m[i][j] += self.m[i][k] * other.m[k][j]
        return result
    
    def transform_point(self, point):
        x = point.x * self.m[0][0] + point.y * self.m[0][1] + point.z * self.m[0][2] + self.m[0][3]
        y = point.x * self.m[1][0] + point.y * self.m[1][1] + point.z * self.m[1][2] + self.m[1][3]
        z = point.x * self.m[2][0] + point.y * self.m[2][1] + point.z * self.m[2][2] + self.m[2][3]
        w = point.x * self.m[3][0] + point.y * self.m[3][1] + point.z * self.m[3][2] + self.m[3][3]
        
        if abs(w) > 0.0001:
            return Vector3D(x/w, y/w, z/w)
        return Vector3D(x, y, z)

class LineDrawing:
    @staticmethod
    def bresenham_line(x1, y1, x2, y2):
        """Bresenham's line drawing algorithm"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        
        x_inc = 1 if x1 < x2 else -1
        y_inc = 1 if y1 < y2 else -1
        
        error = dx - dy
        
        while True:
            points.append((x, y))
            if x == x2 and y == y2:
                break
            
            error2 = 2 * error
            if error2 > -dy:
                error -= dy
                x += x_inc
            if error2 < dx:
                error += dx
                y += y_inc
        
        return points

class Object3D:
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.faces = []
    
    def add_vertex(self, x, y, z):
        self.vertices.append(Vector3D(x, y, z))
        return len(self.vertices) - 1
    
    def add_edge(self, v1_idx, v2_idx):
        self.edges.append((v1_idx, v2_idx))
    
    def add_face(self, vertex_indices):
        self.faces.append(vertex_indices)
    
    def create_cube(self, size=1):
        """Create a cube centered at origin"""
        s = size / 2
        # Define 8 vertices of cube
        vertices = [
            (-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),  # Front face
            (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)       # Back face
        ]
        
        self.vertices = [Vector3D(x, y, z) for x, y, z in vertices]
        
        # Define edges (12 edges for a cube)
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Front face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Back face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]
        
        # Define faces
        self.faces = [
            [0, 1, 2, 3],  # Front
            [4, 7, 6, 5],  # Back
            [0, 4, 7, 3],  # Left
            [1, 5, 6, 2],  # Right
            [0, 1, 5, 4],  # Bottom
            [3, 2, 6, 7]   # Top
        ]
    
    def create_pyramid(self, base_size=1, height=1):
        """Create a pyramid"""
        s = base_size / 2
        h = height / 2
        
        # Define vertices: 4 base vertices + 1 apex
        vertices = [
            (-s, -h, -s), (s, -h, -s), (s, -h, s), (-s, -h, s),  # Base
            (0, h, 0)  # Apex
        ]
        
        self.vertices = [Vector3D(x, y, z) for x, y, z in vertices]
        
        # Define edges
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Base edges
            (0, 4), (1, 4), (2, 4), (3, 4)   # Apex edges
        ]
        
        # Define faces
        self.faces = [
            [0, 3, 2, 1],  # Base
            [0, 1, 4],     # Face 1
            [1, 2, 4],     # Face 2
            [2, 3, 4],     # Face 3
            [3, 0, 4]      # Face 4
        ]

class Camera:
    def __init__(self, position, target, up):
        self.position = position
        self.target = target
        self.up = up
        self.fov = math.pi / 3  # 60 degrees
        self.near = 0.1
        self.far = 100.0
        self.aspect_ratio = 16/9

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.projection_mode = "perspective"  # or "orthographic"
        
    def orthographic_projection(self, point, scale=100):
        """Convert 3D point to 2D using orthographic projection"""
        x = point.x * scale + self.width // 2
        y = -point.y * scale + self.height // 2  # Flip Y axis
        return (int(x), int(y))
    
    def perspective_projection(self, point, camera_distance=5, scale=200):
        """Convert 3D point to 2D using perspective projection"""
        if point.z + camera_distance <= 0:
            return None
        
        perspective_scale = camera_distance / (point.z + camera_distance)
        x = (point.x * perspective_scale * scale) + self.width // 2
        y = -(point.y * perspective_scale * scale) + self.height // 2  # Flip Y axis
        return (int(x), int(y))
    
    def project_point(self, point):
        """Project 3D point to 2D based on current projection mode"""
        if self.projection_mode == "orthographic":
            return self.orthographic_projection(point)
        else:
            return self.perspective_projection(point)
    
    def draw_line_with_algorithm(self, surface, color, start_pos, end_pos):
        """Draw line using Bresenham's algorithm"""
        if start_pos is None or end_pos is None:
            return
        
        points = LineDrawing.bresenham_line(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
        for point in points:
            if 0 <= point[0] < self.width and 0 <= point[1] < self.height:
                surface.set_at(point, color)
    
    def render_object(self, obj, transform_matrix, wireframe=True, filled=False):
        """Render 3D object with transformations and enhanced visuals"""
        # Transform vertices
        transformed_vertices = []
        for vertex in obj.vertices:
            transformed_vertex = transform_matrix.transform_point(vertex)
            transformed_vertices.append(transformed_vertex)
        
        # Project to 2D
        projected_vertices = []
        for vertex in transformed_vertices:
            projected = self.project_point(vertex)
            projected_vertices.append(projected)
        
        # Draw filled faces first (if enabled)
        if filled:
            for i, face in enumerate(obj.faces):
                face_points = []
                valid_face = True
                for vertex_idx in face:
                    if projected_vertices[vertex_idx] is None:
                        valid_face = False
                        break
                    face_points.append(projected_vertices[vertex_idx])
                
                if valid_face and len(face_points) >= 3:
                    # Different colors for different faces
                    colors = [
                        (100, 150, 255, 120),  # Light blue
                        (255, 150, 100, 120),  # Light orange
                        (150, 255, 100, 120),  # Light green
                        (255, 100, 150, 120),  # Light pink
                        (150, 100, 255, 120),  # Light purple
                        (255, 255, 100, 120)   # Light yellow
                    ]
                    face_color = colors[i % len(colors)]
                    
                    try:
                        # Create surface for face with alpha
                        face_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                        pygame.gfxdraw.filled_polygon(face_surface, face_points, face_color)
                        self.screen.blit(face_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
                        
                        # Add face outline
                        if len(face_points) > 2:
                            pygame.draw.polygon(self.screen, (255, 255, 255, 80), face_points, 1)
                    except:
                        pass  # Skip if polygon is invalid
        
        # Draw wireframe with enhanced colors
        if wireframe:
            for edge in obj.edges:
                v1_idx, v2_idx = edge
                start_pos = projected_vertices[v1_idx]
                end_pos = projected_vertices[v2_idx]
                
                if start_pos is not None and end_pos is not None:
                    # Enhanced wireframe colors
                    edge_color = (0, 255, 255)  # Cyan for better visibility
                    
                    # Use pygame's anti-aliased line for smoother appearance
                    pygame.draw.aaline(self.screen, edge_color, start_pos, end_pos, 2)
                    
                    # Add glow effect
                    glow_color = (0, 150, 150, 100)  # Semi-transparent cyan
                    pygame.draw.aaline(self.screen, glow_color, start_pos, end_pos, 4)
        
        # Draw vertices as small circles for better visualization
        if wireframe:
            for projected_vertex in projected_vertices:
                if projected_vertex is not None:
                    # Draw vertex points
                    pygame.draw.circle(self.screen, (255, 255, 0), projected_vertex, 3)  # Yellow vertices
                    pygame.draw.circle(self.screen, (255, 100, 0), projected_vertex, 2)  # Orange center
    
    def toggle_projection(self):
        """Toggle between orthographic and perspective projection"""
        self.projection_mode = "orthographic" if self.projection_mode == "perspective" else "perspective"

class Graphics3DApp:
    def __init__(self):
        self.width = 1200
        self.height = 800
        self.renderer = Renderer(self.width, self.height)
        pygame.display.set_caption("🎮 3D Graphics with Transformations - Mid Semester Project 🎮")
        
        # Set a nice gradient background
        self.background = self.create_gradient_background()
        
        # Create 3D objects
        self.cube = Object3D()
        self.cube.create_cube(2)
        
        self.pyramid = Object3D()
        self.pyramid.create_pyramid(2, 2)
        
        self.current_object = self.cube
        self.object_type = "cube"
        
        # Transformation parameters
        self.rotation_x = 0.3  # Start with slight rotation for better view
        self.rotation_y = 0.3
        self.rotation_z = 0
        self.translation_x = 0
        self.translation_y = 0
        self.translation_z = 0
        self.scale_x = 1
        self.scale_y = 1
        self.scale_z = 1
        
        # Rendering options
        self.wireframe = True
        self.filled = False
        self.auto_rotate = False
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)  # Slightly smaller for better fit
        
        # Animation variables for smooth transitions
        self.animation_time = 0
    
    def create_gradient_background(self):
        """Create a beautiful gradient background"""
        background = pygame.Surface((self.width, self.height))
        
        # Create vertical gradient from dark blue to black
        for y in range(self.height):
            # Gradient from dark blue (top) to black (bottom)
            ratio = y / self.height
            r = int(10 * (1 - ratio))
            g = int(15 * (1 - ratio))
            b = int(30 * (1 - ratio))
            
            color = (r, g, b)
            pygame.draw.line(background, color, (0, y), (self.width, y))
        
        # Add some stars for visual appeal
        import random
        random.seed(42)  # Fixed seed for consistent star positions
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            brightness = random.randint(50, 255)
            size = random.randint(1, 2)
            pygame.draw.circle(background, (brightness, brightness, brightness), (x, y), size)
        
        return background
    
    def get_transform_matrix(self):
        """Calculate combined transformation matrix"""
        # Create individual transformation matrices
        translation = Matrix4x4.translation(self.translation_x, self.translation_y, self.translation_z)
        rotation_x = Matrix4x4.rotation_x(self.rotation_x)
        rotation_y = Matrix4x4.rotation_y(self.rotation_y)
        rotation_z = Matrix4x4.rotation_z(self.rotation_z)
        scaling = Matrix4x4.scaling(self.scale_x, self.scale_y, self.scale_z)
        
        # Combine transformations: Scale -> Rotate -> Translate
        transform = translation.multiply(rotation_z.multiply(rotation_y.multiply(rotation_x.multiply(scaling))))
        return transform
    
    def handle_input(self):
        """Handle keyboard and mouse input"""
        keys = pygame.key.get_pressed()
        
        # Rotation controls
        rotation_speed = 0.02
        if keys[pygame.K_q]: self.rotation_x += rotation_speed
        if keys[pygame.K_a]: self.rotation_x -= rotation_speed
        if keys[pygame.K_w]: self.rotation_y += rotation_speed
        if keys[pygame.K_s]: self.rotation_y -= rotation_speed
        if keys[pygame.K_e]: self.rotation_z += rotation_speed
        if keys[pygame.K_d]: self.rotation_z -= rotation_speed
        
        # Translation controls
        translation_speed = 0.1
        if keys[pygame.K_UP]: self.translation_y += translation_speed
        if keys[pygame.K_DOWN]: self.translation_y -= translation_speed
        if keys[pygame.K_LEFT]: self.translation_x -= translation_speed
        if keys[pygame.K_RIGHT]: self.translation_x += translation_speed
        if keys[pygame.K_PAGEUP]: self.translation_z += translation_speed
        if keys[pygame.K_PAGEDOWN]: self.translation_z -= translation_speed
        
        # Scaling controls
        scale_speed = 0.01
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            self.scale_x += scale_speed
            self.scale_y += scale_speed
            self.scale_z += scale_speed
        if keys[pygame.K_MINUS]:
            self.scale_x = max(0.1, self.scale_x - scale_speed)
            self.scale_y = max(0.1, self.scale_y - scale_speed)
            self.scale_z = max(0.1, self.scale_z - scale_speed)
    
    def draw_ui(self):
        """Draw enhanced user interface with colors and backgrounds"""
        # Colors
        bg_color = (20, 20, 40, 180)  # Semi-transparent dark blue
        title_color = (255, 215, 0)   # Gold
        status_color = (0, 255, 127)  # Spring green
        value_color = (255, 182, 193) # Light pink
        control_color = (173, 216, 230) # Light blue
        header_color = (255, 69, 0)   # Red orange
        
        # Create semi-transparent background panels
        ui_bg = pygame.Surface((580, 320), pygame.SRCALPHA)
        ui_bg.fill(bg_color)
        self.renderer.screen.blit(ui_bg, (5, 5))
        
        controls_bg = pygame.Surface((580, 180), pygame.SRCALPHA)
        controls_bg.fill((40, 20, 40, 180))
        self.renderer.screen.blit(controls_bg, (5, 335))
        
        # Title
        title = self.font.render("🎮 3D GRAPHICS TRANSFORMATIONS", True, title_color)
        self.renderer.screen.blit(title, (15, 15))
        
        # Status information with colors
        status_texts = [
            (f"📦 Object: {self.object_type.upper()}", status_color),
            (f"🎯 Projection: {self.renderer.projection_mode.upper()}", status_color),
            (f"🔄 Auto-Rotate: {'ON' if self.auto_rotate else 'OFF'}", (0, 255, 0) if self.auto_rotate else (255, 100, 100)),
            (f"🖼️  Wireframe: {'ON' if self.wireframe else 'OFF'}", (0, 255, 0) if self.wireframe else (255, 100, 100)),
            (f"🎨 Fill: {'ON' if self.filled else 'OFF'}", (0, 255, 0) if self.filled else (255, 100, 100))
        ]
        
        y_pos = 50
        for text, color in status_texts:
            surface = self.font.render(text, True, color)
            self.renderer.screen.blit(surface, (15, y_pos))
            y_pos += 30
        
        # Transformation values with highlighting
        transform_header = self.font.render("🔧 TRANSFORMATIONS:", True, header_color)
        self.renderer.screen.blit(transform_header, (15, y_pos + 10))
        y_pos += 40
        
        transform_texts = [
            f"🔄 Rotation   → X: {self.rotation_x:.2f}  Y: {self.rotation_y:.2f}  Z: {self.rotation_z:.2f}",
            f"📍 Translation → X: {self.translation_x:.2f}  Y: {self.translation_y:.2f}  Z: {self.translation_z:.2f}",
            f"📏 Scale      → X: {self.scale_x:.2f}  Y: {self.scale_y:.2f}  Z: {self.scale_z:.2f}"
        ]
        
        for text in transform_texts:
            surface = self.font.render(text, True, value_color)
            self.renderer.screen.blit(surface, (15, y_pos))
            y_pos += 25
        
        # Controls section with better formatting
        controls_header = self.font.render("🎮 CONTROLS:", True, header_color)
        self.renderer.screen.blit(controls_header, (15, 345))
        
        control_texts = [
            "🔄 ROTATION    → Q/A: X-axis  |  W/S: Y-axis  |  E/D: Z-axis",
            "📍 TRANSLATION → ↑↓←→: XY plane  |  PgUp/PgDn: Z-axis",
            "📏 SCALING     → +/-: Uniform scale",
            "🔀 TOGGLES     → P: Projection  |  O: Object  |  Space: Wireframe",
            "⚡ SPECIAL     → F: Fill  |  T: Auto-rotate  |  R: Reset  |  ESC: Exit"
        ]
        
        y_pos = 375
        for text in control_texts:
            surface = self.font.render(text, True, control_color)
            self.renderer.screen.blit(surface, (15, y_pos))
            y_pos += 25
        
        # FPS Counter
        fps = int(self.clock.get_fps())
        fps_color = (0, 255, 0) if fps >= 50 else (255, 255, 0) if fps >= 30 else (255, 0, 0)
        fps_text = self.font.render(f"⚡ FPS: {fps}", True, fps_color)
        self.renderer.screen.blit(fps_text, (self.width - 100, 15))
    
    def reset_transformations(self):
        """Reset all transformations to default values"""
        self.rotation_x = self.rotation_y = self.rotation_z = 0
        self.translation_x = self.translation_y = self.translation_z = 0
        self.scale_x = self.scale_y = self.scale_z = 1
    
    def run(self):
        """Main application loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.renderer.toggle_projection()
                    elif event.key == pygame.K_o:
                        if self.object_type == "cube":
                            self.current_object = self.pyramid
                            self.object_type = "pyramid"
                        else:
                            self.current_object = self.cube
                            self.object_type = "cube"
                    elif event.key == pygame.K_r:
                        self.reset_transformations()
                    elif event.key == pygame.K_f:
                        self.filled = not self.filled
                    elif event.key == pygame.K_SPACE:
                        self.wireframe = not self.wireframe
                    elif event.key == pygame.K_t:
                        self.auto_rotate = not self.auto_rotate
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Handle continuous input
            self.handle_input()
            
            # Auto-rotation with smooth animation
            if self.auto_rotate:
                self.animation_time += 0.016  # ~60 FPS timing
                self.rotation_y += 0.01
                self.rotation_x += 0.005
                # Add slight oscillation for more interesting animation
                self.translation_z = 0.5 * math.sin(self.animation_time * 2)
            
            # Clear screen with gradient background
            self.renderer.screen.blit(self.background, (0, 0))
            
            # Add subtle moving grid effect
            self.draw_grid_effect()
            
            # Get transformation matrix and render object
            transform = self.get_transform_matrix()
            self.renderer.render_object(self.current_object, transform, self.wireframe, self.filled)
            
            # Draw UI
            self.draw_ui()
            
            # Add subtle border effect
            pygame.draw.rect(self.renderer.screen, (100, 100, 150), (0, 0, self.width, self.height), 3)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
    
    def draw_grid_effect(self):
        """Draw a subtle animated grid effect in the background"""
        grid_color = (20, 30, 50, 50)  # Very subtle
        grid_size = 50
        offset = int((self.animation_time * 10) % grid_size)
        
        # Vertical lines
        for x in range(-offset, self.width + grid_size, grid_size):
            if x >= 0 and x < self.width:
                pygame.draw.line(self.renderer.screen, grid_color, (x, 0), (x, self.height), 1)
        
        # Horizontal lines
        for y in range(-offset, self.height + grid_size, grid_size):
            if y >= 0 and y < self.height:
                pygame.draw.line(self.renderer.screen, grid_color, (0, y), (self.width, y), 1)

# Main execution
if __name__ == "__main__":
    app = Graphics3DApp()
    app.run()

import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# --- Point and Cube Classes ---
class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def rotate_x(self, angle):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        y = self.y * cos_a - self.z * sin_a
        z = self.y * sin_a + self.z * cos_a
        return Point3D(self.x, y, z)

    def rotate_y(self, angle):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        x = self.x * cos_a + self.z * sin_a
        z = -self.x * sin_a + self.z * cos_a
        return Point3D(x, self.y, z)

    def rotate_z(self, angle):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        return Point3D(x, y, self.z)

    def project_orthogonal(self):
        return (self.x, self.y)

    def project_perspective(self, distance, fov):
        focal_length = distance / math.tan(math.radians(fov) / 2)
        z_effective = self.z + distance
        if z_effective <= 0:
            return None
        scale = focal_length / z_effective
        return (self.x * scale, self.y * scale)

class Cube:
    def __init__(self, size=80):
        s = size
        self.vertices = [
            Point3D(-s, -s, -s), Point3D(s, -s, -s), Point3D(s, s, -s), Point3D(-s, s, -s),
            Point3D(-s, -s, s), Point3D(s, -s, s), Point3D(s, s, s), Point3D(-s, s, s)
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

# --- Slider Class ---
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos = max(self.rect.x, min(self.rect.right, event.pos[0]))
            ratio = (pos - self.rect.x) / self.rect.width
            self.val = self.min_val + ratio * (self.max_val - self.min_val)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 1)
        
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        pygame.draw.circle(screen, WHITE, (int(handle_x), self.rect.centery), 8)
        
        font = pygame.font.Font(None, 20)
        text_surface = font.render(f"{self.label}: {self.val:.1f}", True, WHITE)
        text_rect = text_surface.get_rect(midbottom=(self.rect.centerx, self.rect.top - 5))
        screen.blit(text_surface, text_rect)

# --- Main Functions ---
def draw_projection_view(screen, cube, rotation, view_rect, title, is_perspective, distance, fov):
    screen.fill(BLACK, view_rect)
    pygame.draw.rect(screen, WHITE, view_rect, 1)

    font = pygame.font.Font(None, 24)
    title_surface = font.render(title, True, WHITE)
    title_rect = title_surface.get_rect(center=(view_rect.centerx, view_rect.top + 20))
    screen.blit(title_surface, title_rect)

    center_x, center_y = view_rect.centerx, view_rect.centery

    # Apply all three rotations
    rotated_vertices = [v.rotate_x(rotation[0]).rotate_y(rotation[1]).rotate_z(rotation[2]) for v in cube.vertices]

    for edge in cube.edges:
        v1, v2 = rotated_vertices[edge[0]], rotated_vertices[edge[1]]
        p1_2d, p2_2d = None, None

        if is_perspective:
            proj1 = v1.project_perspective(distance, fov)
            proj2 = v2.project_perspective(distance, fov)
            if proj1 and proj2:
                p1_2d = (center_x + proj1[0], center_y - proj1[1])
                p2_2d = (center_x + proj2[0], center_y - proj2[1])
        else:
            proj1 = v1.project_orthogonal()
            proj2 = v2.project_orthogonal()
            p1_2d = (center_x + proj1[0], center_y - proj1[1])
            p2_2d = (center_x + proj2[0], center_y - proj2[1])
        
        if p1_2d and p2_2d:
            pygame.draw.line(screen, WHITE, p1_2d, p2_2d, 1)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("3D Projection Demo with Full Interactions")
    clock = pygame.time.Clock()

    cube = Cube()
    
    # Sliders for all interactive parameters
    sliders = [
        Slider(50, 520, 200, 10, 0, 360, 0, "Rotation X"),
        Slider(300, 520, 200, 10, 0, 360, 0, "Rotation Y"),
        Slider(550, 520, 200, 10, 0, 360, 0, "Rotation Z"),
        Slider(800, 520, 200, 10, 200, 1000, 400, "Distance"),
        Slider(800, 580, 200, 10, 30, 120, 60, "FOV")
    ]
    
    # Store rotation values
    rotation_angles = [0, 0, 0] # x, y, z

    running = True
    while running:
        # Flag to check if any slider is being dragged
        is_slider_dragging = any(s.dragging for s in sliders)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle events for all sliders
            for slider in sliders:
                slider.handle_event(event)

            # Update rotation angles from sliders
            rotation_angles[0] = math.radians(sliders[0].val)
            rotation_angles[1] = math.radians(sliders[1].val)
            rotation_angles[2] = math.radians(sliders[2].val)

        screen.fill(BLACK)

        # Draw the two projection views
        ortho_rect = pygame.Rect(50, 80, 500, 400)
        draw_projection_view(screen, cube, rotation_angles, ortho_rect, "ORTHOGONAL VIEW", False, 0, 0)

        persp_rect = pygame.Rect(650, 80, 500, 400)
        draw_projection_view(screen, cube, rotation_angles, persp_rect, "PERSPECTIVE VIEW", True, sliders[3].val, sliders[4].val)
        
        # Draw all sliders
        for slider in sliders:
            slider.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
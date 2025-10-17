import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
import math

@dataclass
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        if isinstance(scalar, Vec3):
            return Vec3(self.x * scalar.x, self.y * scalar.y, self.z * scalar.z)
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar):
        if isinstance(scalar, Vec3):
            return Vec3(self.x * scalar.x, self.y * scalar.y, self.z * scalar.z)
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        if isinstance(scalar, Vec3):
            return Vec3(self.x / scalar.x, self.y / scalar.y, self.z / scalar.z)
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        l = self.length()
        return self / l if l > 0 else self

    def to_array(self):
        return np.array([self.x, self.y, self.z])

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3

@dataclass
class Material:
    color: Vec3
    metallic: float
    roughness: float

@dataclass
class Sphere:
    center: Vec3
    radius: float
    material: Material

@dataclass
class HitInfo:
    hit: bool
    t: float
    point: Vec3
    normal: Vec3
    material: Material

class RayTracer:
    def __init__(self, width: int, height: int, samples_per_pixel: int = 4, max_bounces: int = 5):
        self.width = width
        self.height = height
        self.samples_per_pixel = samples_per_pixel
        self.max_bounces = max_bounces
        self.image = np.zeros((height, width, 3))
        self.frame_count = 0

        # Scene setup
        self.spheres = [
            Sphere(Vec3(0, 1, 0), 1.0, Material(Vec3(0.8, 0.2, 0.2), 0.0, 0.2)),
            Sphere(Vec3(-3, 1, -2), 0.8, Material(Vec3(0.2, 0.8, 0.2), 0.5, 0.3)),
            Sphere(Vec3(3, 1, -1), 1.2, Material(Vec3(0.2, 0.2, 0.8), 0.8, 0.1)),
            Sphere(Vec3(0, 0, -4), 0.6, Material(Vec3(0.9, 0.9, 0.1), 1.0, 0.05)),
            Sphere(Vec3(0, -1001, 0), 1000.0, Material(Vec3(0.7, 0.7, 0.7), 0.0, 0.5)),
        ]

        # Camera setup
        self.camera_pos = Vec3(0, 3, 8)
        self.camera_dir = Vec3(0, -0.3, -1).normalize()
        self.camera_up = Vec3(0, 1, 0)
        self.camera_right = self.camera_dir.cross(self.camera_up).normalize()
        self.camera_up = self.camera_right.cross(self.camera_dir).normalize()
        self.fov = 75

    def ray_sphere_intersect(self, ray: Ray, sphere: Sphere) -> HitInfo:
        oc = ray.origin - sphere.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - sphere.radius ** 2
        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            return HitInfo(False, 0, Vec3(0, 0, 0), Vec3(0, 0, 0), None)

        t = (-b - math.sqrt(discriminant)) / (2 * a)
        if t < 0.001:
            t = (-b + math.sqrt(discriminant)) / (2 * a)

        if t > 0.001:
            point = ray.origin + ray.direction * t
            normal = (point - sphere.center).normalize()
            return HitInfo(True, t, point, normal, sphere.material)

        return HitInfo(False, 0, Vec3(0, 0, 0), Vec3(0, 0, 0), None)

    def trace_ray(self, ray: Ray) -> HitInfo:
        closest = HitInfo(False, float('inf'), Vec3(0, 0, 0), Vec3(0, 0, 0), None)

        for sphere in self.spheres:
            hit = self.ray_sphere_intersect(ray, sphere)
            if hit.hit and hit.t < closest.t:
                closest = hit

        return closest

    def evaluate_lighting(self, point: Vec3, normal: Vec3, view_dir: Vec3, material: Material) -> Vec3:
        light_pos = Vec3(5, 8, 5)
        to_light = (light_pos - point).normalize()
        to_view = view_dir.normalize()

        # Ambient
        ambient = material.color * 0.3

        # Diffuse
        diff = max(0, normal.dot(to_light))
        diffuse = material.color * (diff * 0.7)

        # Specular (simplified Cook-Torrance)
        h = (to_light + to_view).normalize()
        spec_exp = 256.0 if material.metallic > 0.5 else 16.0
        spec = (normal.dot(h) ** spec_exp) * material.metallic * 0.8
        specular = Vec3(spec, spec, spec)

        return ambient + diffuse + specular

    def random_in_hemisphere(self, normal: Vec3) -> Vec3:
        theta = 2 * math.pi * np.random.random()
        phi = math.acos(2 * np.random.random() - 1)
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        return Vec3(x, y, z).normalize()

    def path_trace(self, ray: Ray) -> Vec3:
        radiance = Vec3(0, 0, 0)
        throughput = Vec3(1, 1, 1)

        for bounce in range(self.max_bounces):
            hit = self.trace_ray(ray)

            if not hit.hit:
                # Sky gradient
                t = 0.5 * (ray.direction.y + 1.0)
                sky = Vec3(1, 1, 1) * (1 - t) + Vec3(0.5, 0.7, 1) * t
                radiance = radiance + throughput * (sky * 0.3)
                break

            # Direct lighting
            lighting = self.evaluate_lighting(hit.point, hit.normal, ray.direction * -1, hit.material)
            radiance = radiance + throughput * lighting

            # Update throughput
            throughput = throughput * hit.material.color

            # Next ray direction
            random_dir = self.random_in_hemisphere(hit.normal)
            refl_dir = ray.direction - hit.normal * (2 * ray.direction.dot(hit.normal))
            refl_dir = (refl_dir * hit.material.metallic + random_dir * (1 - hit.material.metallic)).normalize()
            refl_dir = (refl_dir + random_dir * hit.material.roughness * 0.3).normalize()

            ray = Ray(hit.point, refl_dir)

            # Russian roulette
            p = max(throughput.x, max(throughput.y, throughput.z))
            if np.random.random() > p:
                break
            throughput = throughput / p

        return radiance

    def render(self):
        print("Starting ray tracing render...")
        for y in range(self.height):
            if y % 50 == 0:
                print(f"Progress: {y}/{self.height}")

            for x in range(self.width):
                pixel_color = Vec3(0, 0, 0)

                for _ in range(self.samples_per_pixel):
                    # Jittered sampling
                    u = (x + np.random.random()) / self.width
                    v = (y + np.random.random()) / self.height

                    # Ray generation
                    aspect = self.width / self.height
                    ndc_x = (u * 2 - 1) * aspect
                    ndc_y = v * 2 - 1

                    fov_rad = math.radians(self.fov / 2)
                    ray_dir = (self.camera_dir +
                               self.camera_right * (ndc_x * math.tan(fov_rad)) +
                               self.camera_up * (ndc_y * math.tan(fov_rad))).normalize()

                    ray = Ray(self.camera_pos, ray_dir)
                    pixel_color = pixel_color + self.path_trace(ray)

                pixel_color = pixel_color / self.samples_per_pixel

                # Tone mapping
                pixel_color = pixel_color / (pixel_color + Vec3(1, 1, 1))
                pixel_color = Vec3(
                    pixel_color.x ** (1/2.2),
                    pixel_color.y ** (1/2.2),
                    pixel_color.z ** (1/2.2)
                )

                self.image[y, x] = np.clip([pixel_color.x, pixel_color.y, pixel_color.z], 0, 1)

        print("Render complete!")

    def display(self):
        plt.figure(figsize=(12, 8))
        plt.imshow(self.image)
        plt.axis('off')
        plt.title('Ray Traced Scene')
        plt.tight_layout()
        plt.show()

    def save(self, filename: str = 'ray_traced_image.png'):
        plt.figure(figsize=(12, 8))
        plt.imshow(self.image)
        plt.axis('off')
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Image saved as {filename}")
        plt.close()

if __name__ == '__main__':
    # Create ray tracer (smaller resolution for faster render)
    tracer = RayTracer(width=800, height=600, samples_per_pixel=8, max_bounces=5)

    # Render the scene
    tracer.render()

    # Display result
    tracer.display()

    # Optionally save to file
    tracer.save('ray_traced_output.png')